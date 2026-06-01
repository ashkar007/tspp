"""
MockProvider — synthetic market data generator for development and testing.

Generates realistic-looking timeseries:
  • Spot prices  — Geometric Brownian Motion
  • Implied vols — Ornstein-Uhlenbeck mean-reversion
  • Realised vols — rolling window on spot log-returns

Each ticker has a deterministic seed so results are reproducible.
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd

from tsil.constants import ExpiryType, StrikeType
from tsil.data.provider import DataProvider
from tsil.types.expiry import Expiry
from tsil.types.strike import Strike


# ---------------------------------------------------------------------------
# Ticker-specific calibration
# ---------------------------------------------------------------------------

_TICKER_PARAMS: dict[str, dict] = {
    # ticker: {spot0, drift, vol, iv_base}
    "SPX":      {"spot0": 5800, "drift": 0.07, "vol": 0.16, "iv_base": 0.16},
    "SX5E":     {"spot0": 4900, "drift": 0.05, "vol": 0.19, "iv_base": 0.19},
    ".STOXX50E":{"spot0": 4900, "drift": 0.05, "vol": 0.19, "iv_base": 0.19},
    "MSFT.O":   {"spot0": 450,  "drift": 0.12, "vol": 0.28, "iv_base": 0.25},
    "AAPL.O":   {"spot0": 220,  "drift": 0.10, "vol": 0.26, "iv_base": 0.24},
    "NKY":      {"spot0": 38000,"drift": 0.04, "vol": 0.22, "iv_base": 0.21},
}

_DEFAULT_PARAMS = {"spot0": 1000, "drift": 0.06, "vol": 0.20, "iv_base": 0.20}


def _params(ticker: str) -> dict:
    return _TICKER_PARAMS.get(ticker, _DEFAULT_PARAMS)


def _seed(ticker: str) -> int:
    """Deterministic seed from ticker name."""
    return int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16)


def _business_dates(start: date, end: date) -> pd.DatetimeIndex:
    """Generate business-day date range."""
    return pd.bdate_range(start=start, end=end)


class MockProvider(DataProvider):
    """Synthetic market data generator."""

    def __init__(
        self,
        default_start: date | None = None,
        default_end: date | None = None,
    ) -> None:
        self._default_start = default_start or date(2024, 1, 2)
        self._default_end = default_end or date(2025, 12, 31)

    # -- spots ---------------------------------------------------------------

    def get_spot(
        self,
        ticker: str,
        start: date | None = None,
        end: date | None = None,
    ) -> pd.Series:
        start = start or self._default_start
        end = end or self._default_end
        dates = _business_dates(start, end)
        n = len(dates)
        p = _params(ticker)
        rng = np.random.RandomState(_seed(ticker))

        dt = 1 / 252
        log_returns = (p["drift"] - 0.5 * p["vol"]**2) * dt + p["vol"] * np.sqrt(dt) * rng.randn(n)
        prices = p["spot0"] * np.exp(np.cumsum(log_returns))

        return pd.Series(prices, index=dates, name=f"SPOT:{ticker}")

    # -- implied vol ---------------------------------------------------------

    def get_implied_vol(
        self,
        ticker: str,
        expiry: Expiry,
        strike: Strike,
        start: date | None = None,
        end: date | None = None,
    ) -> pd.Series:
        start = start or self._default_start
        end = end or self._default_end
        dates = _business_dates(start, end)
        n = len(dates)
        p = _params(ticker)

        # Seed from ticker + expiry + strike for variety
        seed_str = f"{ticker}:{expiry.raw_spec}:{strike._raw}"
        rng = np.random.RandomState(
            int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        )

        # Base IV level
        base = p["iv_base"]

        # Term structure effect: longer tenors → slightly higher IV
        tenor_adj = self._tenor_adjustment(expiry, start)

        # Skew / strike effect
        strike_adj = self._strike_adjustment(strike)

        # Ornstein-Uhlenbeck mean-reverting process
        theta = base + tenor_adj + strike_adj   # long-run mean
        kappa = 5.0                              # mean-reversion speed
        sigma = 0.03                             # vol-of-vol
        dt = 1 / 252

        iv = np.empty(n)
        iv[0] = theta
        for i in range(1, n):
            dw = rng.randn()
            iv[i] = iv[i - 1] + kappa * (theta - iv[i - 1]) * dt + sigma * np.sqrt(dt) * dw

        # Clamp to sensible range
        iv = np.clip(iv, 0.03, 1.50)

        name = f"IV:{ticker}:{expiry.raw_spec}:{strike._raw}"
        return pd.Series(iv, index=dates, name=name)

    # -- realised vol --------------------------------------------------------

    def get_realised_vol(
        self,
        ticker: str,
        window: int = 30,
        start: date | None = None,
        end: date | None = None,
    ) -> pd.Series:
        # Need extra history for the rolling window
        lookback = timedelta(days=int(window * 1.5) + 30)
        eff_start = (start or self._default_start) - lookback
        spot = self.get_spot(ticker, eff_start, end or self._default_end)
        log_ret = np.log(spot / spot.shift(1))
        rv = log_ret.rolling(window).std() * np.sqrt(252)

        # Trim to requested range
        mask = rv.index >= pd.Timestamp(start or self._default_start)
        rv = rv.loc[mask]
        rv.name = f"RV:{ticker}:{window}d"
        return rv

    # -- internal adjustments ------------------------------------------------

    @staticmethod
    def _tenor_adjustment(expiry: Expiry, as_of: date) -> float:
        """Longer tenors have slightly higher IV (typical equity term structure)."""
        try:
            days = expiry.tenor_days(as_of)
        except Exception:
            days = 90  # fallback
        # ~0 for 1M, ~+0.02 for 1Y, ~+0.03 for 2Y
        return 0.02 * (days / 365) ** 0.5

    @staticmethod
    def _strike_adjustment(strike: Strike) -> float:
        """Skew: OTM puts have higher IV, OTM calls have lower IV."""
        st = strike.strike_type
        v = strike.value

        if st == StrikeType.FORWARD_MONEYNESS or st == StrikeType.SPOT_MONEYNESS:
            # 100% = ATM → 0, 90% → +0.04 (put skew), 110% → -0.02 (call)
            return -0.004 * (v - 100.0)

        if st in (StrikeType.DELTA, StrikeType.DELTA_PUT, StrikeType.DELTA_CALL):
            # 50D ≈ ATM, 25D put → skew up, 25D call → skew down
            if st == StrikeType.DELTA_PUT:
                # Lower delta puts → higher IV
                return 0.04 * (1 - v / 50.0)
            elif st == StrikeType.DELTA_CALL:
                return -0.02 * (1 - v / 50.0)
            else:
                # Auto delta: positive → call-like, negative → put-like
                if v < 0:
                    return 0.04 * (1 - abs(v) / 50.0)
                return -0.02 * (1 - v / 50.0)

        # Absolute or normalised — no adjustment
        return 0.0


# ---------------------------------------------------------------------------
# Module-level default provider
# ---------------------------------------------------------------------------

_default_provider: MockProvider | None = None


def get_default_provider() -> MockProvider:
    """Return the module-level default MockProvider (lazily created)."""
    global _default_provider
    if _default_provider is None:
        _default_provider = MockProvider()
    return _default_provider


def set_default_provider(provider: DataProvider) -> None:
    """Replace the module-level default provider (for real API integration)."""
    global _default_provider
    _default_provider = provider  # type: ignore[assignment]
