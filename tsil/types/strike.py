"""
Strike — option exercise-price specification.

Usage:
    k(7500)         # absolute
    k("100%")       # forward moneyness (ATM)
    k("95%S")       # spot moneyness
    k("25D")        # delta (auto)
    k("25DP")       # put delta
    k("25DC")       # call delta
    k("1.5N")       # normalised strike
"""

from __future__ import annotations

import re
from typing import Union

from tsil.constants import StrikeType


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_MONEYNESS_RE     = re.compile(r"^(-?\d+(?:\.\d+)?)%([FS]?)$", re.IGNORECASE)
_DELTA_RE         = re.compile(r"^(-?\d+(?:\.\d+)?)D([PC]?)$", re.IGNORECASE)
_NORMALIZED_RE    = re.compile(r"^(-?\d+(?:\.\d+)?)N$", re.IGNORECASE)


class Strike:
    """Option exercise-price specification."""

    def __init__(self, spec: Union[int, float, str]) -> None:
        if isinstance(spec, (int, float)):
            self._type = StrikeType.ABSOLUTE
            self._value = float(spec)
            self._raw = str(spec)
            return

        if not isinstance(spec, str):
            raise TypeError(
                f"Expected number or string for strike, got {type(spec).__name__}"
            )

        self._raw = spec

        # Forward / Spot Moneyness: "100%", "95%F", "100%S"
        m = _MONEYNESS_RE.match(spec)
        if m:
            self._value = float(m.group(1))
            qualifier = m.group(2).upper()
            if qualifier == "S":
                self._type = StrikeType.SPOT_MONEYNESS
            else:
                # "" or "F" both mean forward moneyness
                self._type = StrikeType.FORWARD_MONEYNESS
            return

        # Delta: "25D", "-25D", "25DP", "25DC"
        m = _DELTA_RE.match(spec)
        if m:
            self._value = float(m.group(1))
            qualifier = m.group(2).upper()
            if qualifier == "P":
                self._type = StrikeType.DELTA_PUT
            elif qualifier == "C":
                self._type = StrikeType.DELTA_CALL
            else:
                self._type = StrikeType.DELTA
            return

        # Normalised: "1.5N"
        m = _NORMALIZED_RE.match(spec)
        if m:
            self._value = float(m.group(1))
            self._type = StrikeType.NORMALIZED
            return

        raise ValueError(f"Cannot parse strike specification: '{spec}'")

    # -- properties ----------------------------------------------------------

    @property
    def strike_type(self) -> StrikeType:
        return self._type

    @property
    def value(self) -> float:
        return self._value

    @property
    def is_atm(self) -> bool:
        """True if this is an ATM strike (100% forward moneyness)."""
        return (
            self._type == StrikeType.FORWARD_MONEYNESS
            and abs(self._value - 100.0) < 1e-9
        )

    # -- dunder --------------------------------------------------------------

    def __repr__(self) -> str:
        if self._type == StrikeType.ABSOLUTE:
            return f"k({self._value:g})"
        return f'k("{self._raw}")'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Strike):
            return NotImplemented
        return self._type == other._type and self._value == other._value

    def __hash__(self) -> int:
        return hash((self._type, self._value))


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def k(spec: Union[int, float, str]) -> Strike:
    """Create a Strike object.

    Args:
        spec: Absolute price (number) or strike string
              (moneyness / delta / normalised).

    Returns:
        A Strike object.

    Examples:
        >>> k(7500)
        k(7500)
        >>> k("100%")
        k("100%")
        >>> k("25DC")
        k("25DC")
    """
    return Strike(spec)
