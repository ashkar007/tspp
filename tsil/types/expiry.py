"""
Expiry — derivative maturity specification.

Supports three modes:
    Fixed:   e("2026-12-17"), e("DEC2026"), e("Z26")
    Tenor:   e("3M"), e("1Y"), e("2D")
    Forward: e("1Y", "6M"), e("Z26", "Z27")
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional, Union

from tsil.constants import (
    EXPIRY_MONTH_CODES,
    MONTH_NAME_TO_NUM,
    ExpiryType,
)


# ---------------------------------------------------------------------------
# Regex patterns for parsing expiry strings
# ---------------------------------------------------------------------------

_ISO_DATE_RE   = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TENOR_RE      = re.compile(r"^(\d+)([DBWMY])$", re.IGNORECASE)
_MONTH_YEAR_RE = re.compile(r"^([A-Z]{3})(\d{2,4})$", re.IGNORECASE)
_LISTED_CODE_RE = re.compile(r"^([FGHJKMNQUVXZ])(\d{2})$", re.IGNORECASE)


class Expiry:
    """Derivative expiry / maturity specification."""

    def __init__(
        self,
        spec: str,
        duration: Optional[str] = None,
    ) -> None:
        self._raw_spec = spec
        self._raw_duration = duration

        if duration is not None:
            self._type = ExpiryType.FORWARD
            self._start = _parse_single(spec)
            self._duration = _parse_single(duration)
        else:
            parsed = _parse_single(spec)
            self._type = parsed["type"]
            self._start = parsed
            self._duration = None

    # -- properties ----------------------------------------------------------

    @property
    def expiry_type(self) -> ExpiryType:
        return self._type

    @property
    def is_tenor(self) -> bool:
        return self._type == ExpiryType.TENOR

    @property
    def is_fixed(self) -> bool:
        return self._type == ExpiryType.FIXED

    @property
    def is_forward(self) -> bool:
        return self._type == ExpiryType.FORWARD

    @property
    def raw_spec(self) -> str:
        return self._raw_spec

    @property
    def raw_duration(self) -> Optional[str]:
        return self._raw_duration

    # -- resolution ----------------------------------------------------------

    def resolve(self, as_of: date | None = None) -> date:
        """Resolve to a concrete calendar date.

        For tenors this computes the target date relative to *as_of*
        (defaults to today).  For fixed expiries it returns the parsed date.
        For forward expiries it returns the end date (start + duration).
        """
        if as_of is None:
            as_of = date.today()

        start_date = _resolve_parsed(self._start, as_of)

        if self._duration is not None:
            return _resolve_parsed(self._duration, start_date)
        return start_date

    def tenor_days(self, as_of: date | None = None) -> int:
        """Approximate number of calendar days for this expiry."""
        if as_of is None:
            as_of = date.today()
        resolved = self.resolve(as_of)
        return (resolved - as_of).days

    # -- dunder --------------------------------------------------------------

    def __repr__(self) -> str:
        if self._raw_duration:
            return f'e("{self._raw_spec}", "{self._raw_duration}")'
        return f'e("{self._raw_spec}")'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expiry):
            return NotImplemented
        return (
            self._raw_spec == other._raw_spec
            and self._raw_duration == other._raw_duration
        )

    def __hash__(self) -> int:
        return hash((self._raw_spec, self._raw_duration))


# ---------------------------------------------------------------------------
# Internal parsing helpers
# ---------------------------------------------------------------------------

def _parse_single(spec: str) -> dict:
    """Parse a single expiry/tenor string into a structured dict."""

    # ISO date: 2026-12-17
    if _ISO_DATE_RE.match(spec):
        parts = spec.split("-")
        d = date(int(parts[0]), int(parts[1]), int(parts[2]))
        return {"type": ExpiryType.FIXED, "date": d, "raw": spec}

    # Tenor: 3M, 1Y, 2D, 1W, etc.
    m = _TENOR_RE.match(spec)
    if m:
        units = int(m.group(1))
        period = m.group(2).upper()
        return {
            "type": ExpiryType.TENOR,
            "units": units,
            "period": period,
            "raw": spec,
        }

    # Month-Year: DEC2026, JUN25
    m = _MONTH_YEAR_RE.match(spec)
    if m:
        month_str = m.group(1).upper()
        year_str = m.group(2)
        month = MONTH_NAME_TO_NUM.get(month_str)
        if month is None:
            raise ValueError(f"Unknown month abbreviation: {month_str}")
        year = int(year_str)
        if year < 100:
            year += 2000
        # Use third Friday as a conventional options expiry
        d = _third_friday(year, month)
        return {"type": ExpiryType.FIXED, "date": d, "raw": spec}

    # Listed code: Z26, H25
    m = _LISTED_CODE_RE.match(spec)
    if m:
        code = m.group(1).upper()
        year = int(m.group(2)) + 2000
        month = EXPIRY_MONTH_CODES[code]
        d = _third_friday(year, month)
        return {"type": ExpiryType.FIXED, "date": d, "raw": spec}

    raise ValueError(f"Cannot parse expiry specification: '{spec}'")


def _resolve_parsed(parsed: dict, as_of: date) -> date:
    """Convert a parsed dict into a concrete date."""
    if parsed["type"] == ExpiryType.FIXED:
        return parsed["date"]

    # Tenor
    units = parsed["units"]
    period = parsed["period"]

    if period in ("D", "B"):
        # Business days — approximate by skipping weekends
        result = as_of
        added = 0
        while added < units:
            result += timedelta(days=1)
            if result.weekday() < 5:  # Mon-Fri
                added += 1
        return result
    elif period == "W":
        return as_of + timedelta(weeks=units)
    elif period == "M":
        month = as_of.month - 1 + units
        year = as_of.year + month // 12
        month = month % 12 + 1
        # Clamp day to valid range
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(as_of.day, max_day)
        return date(year, month, day)
    elif period == "Y":
        import calendar
        year = as_of.year + units
        max_day = calendar.monthrange(year, as_of.month)[1]
        day = min(as_of.day, max_day)
        return date(year, as_of.month, day)
    else:
        raise ValueError(f"Unknown period code: {period}")


def _third_friday(year: int, month: int) -> date:
    """Return the third Friday of *month* in *year*."""
    # First day of month
    first = date(year, month, 1)
    # weekday(): Monday=0 … Friday=4
    # Days until first Friday
    days_until_friday = (4 - first.weekday()) % 7
    first_friday = first + timedelta(days=days_until_friday)
    return first_friday + timedelta(weeks=2)


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def e(
    spec: str,
    duration: Optional[str] = None,
) -> Expiry:
    """Create an Expiry (fixed date, tenor, or forward).

    Args:
        spec:     Expiry specification string — ISO date, month-year,
                  listed code, or tenor.
        duration: Optional second parameter for forward expiries.

    Returns:
        An Expiry object.

    Examples:
        >>> e("3M")
        e("3M")
        >>> e("Z26")
        e("Z26")
        >>> e("1Y", "6M")
        e("1Y", "6M")
    """
    return Expiry(spec, duration)
