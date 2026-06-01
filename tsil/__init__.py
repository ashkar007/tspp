"""
TSIL — Timeseries Intermediate Language
A domain-specific language for financial market timeseries analytics.

Usage (direct Python):
    from tsil import t, e, k, IV, RV, WGT_VOL

    vol = IV(t("SPX"), e("3M"), k("100%"))
    rv  = RV(t("SPX"), 30)
    basket = IV(t(["SPX", "SX5E"], WGT_VOL), e("1Y"), k("100%"))
    slope = IV(t("SPX"), e("1Y"), k("100%")) - vol

Usage (string-based engine):
    from tsil import Engine

    engine = Engine()
    result = engine.eval('IV(t("SPX"), e("3M"), k("100%"))')

    # Get AST as dict for REST API transport
    ast_dict = engine.parse_to_dict('IV(t("SPX"), e("3M"), k("100%"))')
"""

__version__ = "0.1.0"

# ── Core types ──────────────────────────────────────────────────────────────
from tsil.types.ticker import t, Ticker
from tsil.types.expiry import e, Expiry
from tsil.types.strike import k, Strike
from tsil.types.timeseries import make_series, get_meta, copy_meta, series_repr, display

# ── Constants ───────────────────────────────────────────────────────────────
from tsil.constants import WGT_EQ, WGT_VOL, WGT_MOM, WGT_MCAP, WeightScheme

# ── Metrics ─────────────────────────────────────────────────────────────────
from tsil.metrics.implied_vol import IV
from tsil.metrics.realised_vol import RV

# ── Operations / Functions ──────────────────────────────────────────────────
from tsil.operations.functions import (
    sqrt,
    diff,
    pct_change,
    corr,
    cov,
    std,
    mean,
    ts_sum,
    ts_min,
    ts_max,
    sharpe,
    drawdown,
    mode,
    percentile,
    pow,
)
from tsil.operations.plot import plot

# ── Engine ──────────────────────────────────────────────────────────────────
from tsil.engine.interpreter import Engine
from tsil.engine.serializer import ast_to_dict, ast_to_json, dict_to_ast, json_to_ast

# ── Data (for advanced users who want to swap providers) ────────────────────
from tsil.data.provider import DataProvider
from tsil.data.mock_provider import MockProvider, set_default_provider

__all__ = [
    # Version
    "__version__",
    # Types
    "t", "Ticker",
    "e", "Expiry",
    "k", "Strike",
    "make_series", "get_meta", "copy_meta", "series_repr", "display",
    # Constants
    "WGT_EQ", "WGT_VOL", "WGT_MOM", "WGT_MCAP", "WeightScheme",
    # Metrics
    "IV", "RV",
    # Operations
    "sqrt", "diff", "pct_change", "corr", "cov",
    "std", "mean", "ts_sum", "ts_min", "ts_max",
    "sharpe", "drawdown", "mode", "percentile", "pow",
    # Plotting
    "plot",
    # Engine
    "Engine",
    # Serialization
    "ast_to_dict", "ast_to_json", "dict_to_ast", "json_to_ast",
    # Data
    "DataProvider", "MockProvider", "set_default_provider",
]
