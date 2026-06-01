"""
TSIL mathematical / statistical functions.

All functions accept ``pd.Series`` objects (with TSIL ``.attrs``)
and return ``pd.Series`` objects, preserving metadata through ``.attrs``.

Usage:
    from tsil.operations.functions import sqrt, corr, sharpe, drawdown
    result = sharpe(ts, window=252)
"""

from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd

from tsil.types.timeseries import copy_meta, make_series


def _result(source: pd.Series, data: pd.Series, name: str) -> pd.Series:
    """Create a result Series preserving source attrs."""
    s = data.copy()
    s.name = name
    s.attrs.update(source.attrs)
    return s


# ---------------------------------------------------------------------------
# Element-wise transforms
# ---------------------------------------------------------------------------

def sqrt(ts: pd.Series) -> pd.Series:
    """Element-wise square root."""
    return _result(ts, np.sqrt(ts), f"sqrt({ts.name})")


def diff(ts: pd.Series, periods: int = 1) -> pd.Series:
    """Difference of timeseries by *periods*."""
    periods = int(periods)
    return _result(ts, ts.diff(periods), f"diff({ts.name}, {periods})")


def pct_change(ts: pd.Series, periods: int = 1) -> pd.Series:
    """Percentage change of timeseries by *periods*."""
    periods = int(periods)
    return _result(ts, ts.pct_change(periods), f"pct_change({ts.name}, {periods})")


# ---------------------------------------------------------------------------
# Rolling window functions
# ---------------------------------------------------------------------------

def corr(ts1: pd.Series, ts2: pd.Series, window: int) -> pd.Series:
    """Rolling correlation between two timeseries."""
    window = int(window)
    result = ts1.rolling(window).corr(ts2)
    return _result(ts1, result, f"corr({ts1.name}, {ts2.name}, {window})")


def cov(ts1: pd.Series, ts2: pd.Series, window: int) -> pd.Series:
    """Rolling covariance between two timeseries."""
    window = int(window)
    result = ts1.rolling(window).cov(ts2)
    return _result(ts1, result, f"cov({ts1.name}, {ts2.name}, {window})")


def std(ts: pd.Series, window: int) -> pd.Series:
    """Rolling standard deviation."""
    window = int(window)
    return _result(ts, ts.rolling(window).std(), f"std({ts.name}, {window})")


def mean(ts: pd.Series, window: int) -> pd.Series:
    """Rolling mean."""
    window = int(window)
    return _result(ts, ts.rolling(window).mean(), f"mean({ts.name}, {window})")


def ts_sum(ts: pd.Series, window: int) -> pd.Series:
    """Rolling sum.

    Named ``ts_sum`` to avoid shadowing Python's built-in ``sum``.
    The parser maps ``sum(...)`` to this function.
    """
    window = int(window)
    return _result(ts, ts.rolling(window).sum(), f"sum({ts.name}, {window})")


def ts_min(ts: pd.Series, window: int) -> pd.Series:
    """Rolling minimum."""
    window = int(window)
    return _result(ts, ts.rolling(window).min(), f"min({ts.name}, {window})")


def ts_max(ts: pd.Series, window: int) -> pd.Series:
    """Rolling maximum."""
    window = int(window)
    return _result(ts, ts.rolling(window).max(), f"max({ts.name}, {window})")


def sharpe(ts: pd.Series, window: int) -> pd.Series:
    """Rolling Sharpe ratio (annualised).

    Computes  mean(daily return) / std(daily return) × √252
    over the specified rolling window.
    """
    window = int(window)
    returns = ts.pct_change()
    rolling_mean = returns.rolling(window).mean()
    rolling_std = returns.rolling(window).std()
    result = (rolling_mean / rolling_std) * np.sqrt(252)
    return _result(ts, result, f"sharpe({ts.name}, {window})")


def drawdown(ts: pd.Series, window: int) -> pd.Series:
    """Rolling drawdown from peak.

    Computed as  (current − rolling_max) / rolling_max  over *window*.
    Values are ≤ 0  (0 = at peak).
    """
    window = int(window)
    rolling_peak = ts.rolling(window, min_periods=1).max()
    dd = (ts - rolling_peak) / rolling_peak
    return _result(ts, dd, f"drawdown({ts.name}, {window})")


# ---------------------------------------------------------------------------
# Scalar / aggregate functions
# ---------------------------------------------------------------------------

def mode(ts: pd.Series) -> pd.Series:
    """Mode of the timeseries (returns a single-element Series)."""
    m = ts.mode()
    m.attrs.update(ts.attrs)
    m.name = f"mode({ts.name})"
    return m


def percentile(ts: pd.Series, q: float) -> float:
    """Percentile of the timeseries.

    Args:
        q: Percentile in [0, 100].

    Returns:
        The percentile value as a float.
    """
    return float(ts.quantile(q / 100.0))


def pow(ts: pd.Series, exponent: Union[int, float]) -> pd.Series:
    """Raise timeseries to a power."""
    return _result(ts, ts ** exponent, f"pow({ts.name}, {exponent})")
