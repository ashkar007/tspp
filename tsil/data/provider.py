"""
DataProvider — abstract interface for market data backends.

Subclass this to plug in real data sources (Bloomberg, Refinitiv, etc.).
The mock provider ships with TSIL for development and testing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

import pandas as pd

from tsil.types.expiry import Expiry
from tsil.types.strike import Strike


class DataProvider(ABC):
    """Abstract base class for TSIL data backends."""

    @abstractmethod
    def get_spot(
        self,
        ticker: str,
        start: date,
        end: date,
    ) -> pd.Series:
        """Return daily spot prices for *ticker* between *start* and *end*.

        Returns:
            pandas.Series indexed by datetime with float values.
        """
        ...

    @abstractmethod
    def get_implied_vol(
        self,
        ticker: str,
        expiry: Expiry,
        strike: Strike,
        start: date,
        end: date,
    ) -> pd.Series:
        """Return daily implied-volatility levels.

        Args:
            ticker:  Single instrument identifier.
            expiry:  Expiry specification (tenor, fixed, or forward).
            strike:  Strike specification.
            start:   Start date (inclusive).
            end:     End date (inclusive).

        Returns:
            pandas.Series indexed by datetime with IV as decimal
            (e.g. 0.18 = 18%).
        """
        ...

    @abstractmethod
    def get_realised_vol(
        self,
        ticker: str,
        window: int,
        start: date,
        end: date,
    ) -> pd.Series:
        """Return daily realised-volatility levels.

        Used by weighting schemes (WGT_VOL) to compute inverse-vol
        weights.

        Args:
            ticker:  Single instrument identifier.
            window:  Look-back window in business days.
            start:   Start date (inclusive).
            end:     End date (inclusive).

        Returns:
            pandas.Series indexed by datetime with annualised realised
            vol as decimal.
        """
        ...
