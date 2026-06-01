"""
RV — Realised Volatility metric.

Computes realised (historical) volatility timeseries from spot price
returns using a close-to-close model.

Returns ``pd.Series`` with metadata in ``.attrs``.

Usage:
    RV(t("SPX"), 30)            # 30-day realised vol
    RV(t("SPX"), 60)            # 60-day realised vol
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from tsil.data.mock_provider import get_default_provider
from tsil.data.provider import DataProvider
from tsil.types.ticker import Ticker
from tsil.types.timeseries import make_series


def RV(
    ticker: Ticker,
    window: int = 30,
    provider: DataProvider | None = None,
) -> pd.Series:
    """Compute realised-volatility timeseries (close-to-close).

    Args:
        ticker:   Ticker object (single instrument — baskets not yet
                  supported for RV).
        window:   Look-back window in business days.
        provider: Optional DataProvider.  Falls back to the default
                  MockProvider if not supplied.

    Returns:
        ``pd.Series`` of annualised realised-vol values indexed by date,
        with TSIL metadata stored in ``.attrs``.

    Examples:
        >>> from tsil import t, RV
        >>> rv = RV(t("SPX"), 30)
        >>> rv.attrs["metric"]
        'RV'
    """
    if provider is None:
        provider = get_default_provider()

    meta = {
        "metric": "RV",
        "ticker": repr(ticker),
        "window": window,
    }

    if not ticker.is_basket:
        series = provider.get_realised_vol(
            ticker.tickers[0], window=window
        )
        return make_series(series, **meta)

    # Basket: compute RV per constituent, then equal-weight average
    # (more sophisticated weighting could be added later)
    rv_parts: list[pd.Series] = []
    for tkr in ticker.tickers:
        s = provider.get_realised_vol(tkr, window=window)
        rv_parts.append(s)

    df = pd.concat(rv_parts, axis=1).dropna()

    # Simple equal-weight average across constituents
    n = len(ticker.tickers)
    averaged = df.mean(axis=1)
    averaged.name = f"RV:basket:{window}d"

    return make_series(averaged, **meta)
