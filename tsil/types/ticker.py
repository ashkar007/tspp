"""
Ticker — represents one or more financial instruments.

Usage:
    t("SPX")                              # single ticker
    t(["SPX", "SX5E"])                    # equal-weighted basket
    t(["SPX", "SX5E"], WGT_VOL)          # volatility-weighted basket
    t(["SPX", "SX5E"], [0.3, 0.7])       # custom-weighted basket
"""

from __future__ import annotations

from typing import Union

from tsil.constants import WeightScheme, WGT_EQ


class Ticker:
    """A financial instrument or weighted basket of instruments."""

    def __init__(
        self,
        tickers: Union[str, list[str]],
        weights: Union[WeightScheme, list[float], None] = None,
    ) -> None:
        # Normalise single ticker to list
        if isinstance(tickers, str):
            self._tickers = [tickers]
        elif isinstance(tickers, list):
            if not tickers:
                raise ValueError("Ticker list must not be empty.")
            self._tickers = list(tickers)
        else:
            raise TypeError(
                f"Expected str or list[str] for tickers, got {type(tickers).__name__}"
            )

        # Resolve weights
        if weights is None:
            self._weight_scheme: WeightScheme | None = WGT_EQ
            self._weights: list[float] | None = None
        elif isinstance(weights, WeightScheme):
            self._weight_scheme = weights
            self._weights = None
        elif isinstance(weights, list):
            if len(weights) != len(self._tickers):
                raise ValueError(
                    f"Weight list length ({len(weights)}) must match "
                    f"ticker list length ({len(self._tickers)})."
                )
            if abs(sum(weights) - 1.0) > 1e-6:
                raise ValueError(
                    f"Weights must sum to 1.0, got {sum(weights):.6f}."
                )
            self._weight_scheme = None
            self._weights = list(weights)
        else:
            raise TypeError(
                f"Expected WeightScheme or list[float] for weights, "
                f"got {type(weights).__name__}"
            )

    # -- properties ----------------------------------------------------------

    @property
    def tickers(self) -> list[str]:
        """List of ticker identifiers."""
        return list(self._tickers)

    @property
    def is_basket(self) -> bool:
        """True if this represents multiple instruments."""
        return len(self._tickers) > 1

    @property
    def weight_scheme(self) -> WeightScheme | None:
        """The named weight scheme, or None if custom weights are used."""
        return self._weight_scheme

    @property
    def weights(self) -> list[float] | None:
        """Explicit numeric weights, or None if a named scheme is used."""
        return list(self._weights) if self._weights is not None else None

    def get_equal_weights(self) -> list[float]:
        """Return equal weights for all tickers."""
        n = len(self._tickers)
        return [1.0 / n] * n

    # -- dunder --------------------------------------------------------------

    def __repr__(self) -> str:
        if not self.is_basket:
            return f't("{self._tickers[0]}")'
        w = self._weight_scheme.value if self._weight_scheme else self._weights
        return f"t({self._tickers}, {w})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ticker):
            return NotImplemented
        return (
            self._tickers == other._tickers
            and self._weight_scheme == other._weight_scheme
            and self._weights == other._weights
        )

    def __hash__(self) -> int:
        w = (
            self._weight_scheme
            if self._weight_scheme
            else tuple(self._weights) if self._weights else None
        )
        return hash((tuple(self._tickers), w))


# ---------------------------------------------------------------------------
# Factory function  (so users write  t("SPX")  not  Ticker("SPX"))
# ---------------------------------------------------------------------------

def t(
    tickers: Union[str, list[str]],
    weights: Union[WeightScheme, list[float], None] = None,
) -> Ticker:
    """Create a Ticker (single instrument or weighted basket).

    Args:
        tickers: Single ticker string or list of ticker strings.
        weights: Optional — a WeightScheme enum or list of numeric weights.
                 Defaults to equal-weighting (WGT_EQ).

    Returns:
        A Ticker object.

    Examples:
        >>> t("SPX")
        t("SPX")
        >>> t(["SPX", "SX5E"], [0.3, 0.7])
        t(['SPX', 'SX5E'], [0.3, 0.7])
    """
    return Ticker(tickers, weights)
