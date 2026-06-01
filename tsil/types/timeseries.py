"""
Timeseries utilities — helpers for working with TSIL-enriched pandas Series.

TSIL uses plain ``pandas.Series`` objects as its primary data type.
Metadata (metric, ticker, expiry, strike) is stored in ``Series.attrs``,
which is a built-in pandas dict for arbitrary metadata.

This module provides:
  • ``make_series()`` — create a pd.Series with TSIL metadata in .attrs
  • ``get_meta()``    — read metadata from a Series
  • ``copy_meta()``   — propagate metadata through operations
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd


def make_series(
    data: pd.Series,
    name: Optional[str] = None,
    **meta: Any,
) -> pd.Series:
    """Wrap a pandas Series with TSIL metadata stored in ``.attrs``.

    Args:
        data:  The raw pandas Series (will be copied).
        name:  Optional name for the Series.
        **meta: Arbitrary metadata keys (metric, ticker, expiry, strike, …).

    Returns:
        A *new* pandas Series with ``.attrs`` populated.

    Example:
        >>> s = make_series(raw, name="IV:SPX:3M:100%",
        ...                 metric="IV", ticker="SPX",
        ...                 expiry="3M", strike="100%")
        >>> s.attrs["metric"]
        'IV'
    """
    s = data.copy()
    s.name = name or data.name
    s.attrs.update(meta)
    return s


def get_meta(series: pd.Series) -> dict[str, Any]:
    """Return a copy of the TSIL metadata dict from a Series."""
    return dict(series.attrs)


def copy_meta(source: pd.Series, target: pd.Series) -> pd.Series:
    """Copy TSIL attrs from *source* onto *target* (in-place + returned)."""
    target.attrs.update(source.attrs)
    return target


def series_repr(series: pd.Series, max_rows: int = 5) -> str:
    """Pretty-print a TSIL-enriched Series.

    Shows metadata header, then the first *max_rows* values.
    """
    meta = series.attrs
    meta_parts = []
    for key in ("metric", "ticker", "expiry", "strike", "window"):
        if key in meta:
            meta_parts.append(f"{key}={meta[key]!r}")
    header = f"Timeseries({', '.join(meta_parts)})" if meta_parts else "Timeseries"

    if len(series) == 0:
        return f"{header}\n(empty)"

    preview = series.head(max_rows).to_string()
    tail_msg = (
        f"\n... ({len(series)} rows total)" if len(series) > max_rows else ""
    )
    return f"{header}\n{preview}{tail_msg}"


def display(series: pd.Series, max_rows: int = 10) -> None:
    """Print a TSIL-enriched Series to stdout."""
    print(series_repr(series, max_rows=max_rows))
