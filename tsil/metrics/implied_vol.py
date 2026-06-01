"""
IV — Implied Volatility metric.

Fetches implied-vol timeseries for a ticker (single or basket),
expiry, and strike from the configured data provider.

Returns ``pd.Series`` with metadata in ``.attrs``.

Usage:
    IV(t("SPX"), e("3M"), k("100%"))
    IV(t(["SPX","SX5E"], [0.6, 0.4]), e("1Y"), k("25DC"))
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from tsil.constants import WeightScheme
from tsil.data.mock_provider import get_default_provider
from tsil.data.provider import DataProvider
from tsil.types.expiry import Expiry
from tsil.types.strike import Strike
from tsil.types.ticker import Ticker
from tsil.types.timeseries import make_series


def IV(
    ticker: Ticker,
    expiry: Expiry,
    strike: Strike,
    provider: DataProvider | None = None,
) -> pd.Series:
    """Fetch implied-volatility timeseries.

    Args:
        ticker:   Ticker object (single or basket).
        expiry:   Expiry object (fixed, tenor, or forward).
        strike:   Strike object.
        provider: Optional DataProvider.  Falls back to the default
                  MockProvider if not supplied.

    Returns:
        ``pd.Series`` of implied-vol values indexed by date, with
        TSIL metadata stored in ``.attrs``.

    Examples:
        >>> from tsil import t, e, k, IV
        >>> vol = IV(t("SPX"), e("3M"), k("100%"))
        >>> vol.attrs["metric"]
        'IV'
    """
    if provider is None:
        provider = get_default_provider()

    meta = {
        "metric": "IV",
        "ticker": repr(ticker),
        "expiry": repr(expiry),
        "strike": repr(strike),
    }

    if not ticker.is_basket:
        # Single ticker — simple fetch
        series = provider.get_implied_vol(
            ticker.tickers[0], expiry, strike
        )
        return make_series(series, **meta)

    # Basket — fetch each constituent then weight
    constituent_series: list[pd.Series] = []
    for tkr in ticker.tickers:
        s = provider.get_implied_vol(tkr, expiry, strike)
        constituent_series.append(s)

    # Align on common dates
    df = pd.concat(constituent_series, axis=1).dropna()

    weights = _resolve_weights(ticker, provider)

    # Weighted average
    weighted = df.multiply(weights, axis=1).sum(axis=1)
    weighted.name = f"IV:basket:{expiry.raw_spec}:{strike._raw}"

    return make_series(weighted, **meta)


def _resolve_weights(
    ticker: Ticker,
    provider: DataProvider,
) -> list[float]:
    """Resolve weight scheme to numeric weights."""
    if ticker.weights is not None:
        return ticker.weights

    scheme = ticker.weight_scheme
    n = len(ticker.tickers)

    if scheme == WeightScheme.EQ:
        return [1.0 / n] * n

    if scheme == WeightScheme.VOL:
        # Inverse-volatility weighting
        vols = []
        for tkr in ticker.tickers:
            rv = provider.get_realised_vol(tkr, window=60)
            mean_rv = rv.dropna().mean()
            vols.append(mean_rv if mean_rv > 0 else 0.20)
        inv_vols = [1.0 / v for v in vols]
        total = sum(inv_vols)
        return [iv / total for iv in inv_vols]

    if scheme == WeightScheme.MOM:
        # Momentum-weighted: weight by trailing 12-month return
        returns = []
        for tkr in ticker.tickers:
            spot = provider.get_spot(tkr)
            if len(spot) > 252:
                ret = spot.iloc[-1] / spot.iloc[-252] - 1
            else:
                ret = spot.iloc[-1] / spot.iloc[0] - 1
            returns.append(max(ret, 0.01))  # floor at small positive
        total = sum(returns)
        return [r / total for r in returns]

    if scheme == WeightScheme.MCAP:
        # Market-cap weighted — approximate by spot level
        spots = []
        for tkr in ticker.tickers:
            s = provider.get_spot(tkr)
            spots.append(s.iloc[-1])
        total = sum(spots)
        return [s / total for s in spots]

    # Fallback
    return [1.0 / n] * n
