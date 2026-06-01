# TSIL — Timeseries Intermediate Language

A domain-specific language (DSL) for financial market timeseries analytics, built in Python.

TSIL provides a high-level, expressive syntax for querying, generating, and analyzing market data and custom signals. It abstracts away the complexity of financial data manipulation while maintaining precision and flexibility for sophisticated analytics.

## Installation

```bash
pip install -e .

# With dev dependencies (pytest)
pip install -e ".[dev]"
```

## Quick Start

### Direct Python Usage

```python
from tsil import t, e, k, IV, WGT_VOL

# Single ticker: SPX 3-month ATM implied volatility
vol = IV(t("SPX"), e("3M"), k("100%"))
print(vol)

# Weighted basket: vol-weighted SPX + SX5E
basket_vol = IV(t(["SPX", "SX5E"], WGT_VOL), e("1Y"), k("100%"))

# Volatility term structure slope
slope = IV(t("SPX"), e("1Y"), k("100%")) - IV(t("SPX"), e("1M"), k("100%"))

# Skew analysis
atm   = IV(t("SPX"), e("3M"), k("100%"))
put25 = IV(t("SPX"), e("3M"), k("25DP"))
skew  = put25 - atm
```

### Interactive REPL

```bash
python -m tsil
```

```
tsil> spx = t("SPX")
tsil> vol = IV(spx, e("3M"), k("100%"))
tsil> vol
Timeseries(ticker='t("SPX")', expiry='e("3M")', strike='k("100%")')
2024-01-02    0.1601
2024-01-03    0.1598
...
(502 rows total)
```

### String-Based Evaluation

```python
from tsil import Engine

engine = Engine()
result = engine.eval('IV(t("SPX"), e("3M"), k("100%"))')
```

## Core Concepts

| Object | Syntax | Description |
|--------|--------|-------------|
| **Ticker** | `t("SPX")` | Single financial instrument |
| **Basket** | `t(["SPX", "SX5E"], WGT_VOL)` | Weighted basket of instruments |
| **Expiry** | `e("3M")`, `e("Z26")` | Tenor or fixed expiry date |
| **Forward** | `e("1Y", "6M")` | Forward-starting expiry |
| **Strike** | `k("100%")`, `k("25DC")` | Strike specification |
| **IV** | `IV(ticker, expiry, strike)` | Implied volatility timeseries |

## Operations

Timeseries support full arithmetic (`+`, `-`, `*`, `/`, `**`) and rolling statistical functions:

```python
from tsil import sharpe, corr, drawdown, std

# Rolling Sharpe ratio (annualised)
sr = sharpe(vol, window=252)

# Rolling correlation
rho = corr(vol1, vol2, window=60)

# Drawdown from peak
dd = drawdown(vol, window=252)
```

## Plugging In Real Data

Replace the mock data provider with your own:

```python
from tsil import DataProvider, set_default_provider

class MyProvider(DataProvider):
    def get_spot(self, ticker, start, end): ...
    def get_implied_vol(self, ticker, expiry, strike, start, end): ...
    def get_realised_vol(self, ticker, window, start, end): ...

set_default_provider(MyProvider())
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
```

## License

Apache 2.0
