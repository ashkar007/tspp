# Timeseries Intermediate Language (TSIL)

## Overview

**TSIL** is a domain-specific language (DSL) designed for financial market timeseries analytics. It provides a high-level, expressive syntax for querying, generating, and analyzing market data and custom signals. TSIL abstracts away the complexity of financial data manipulation while maintaining precision and flexibility for sophisticated analytics.

### Key Features

- **Intuitive Syntax**: Write complex financial queries in a readable, concise manner
- **Composable Objects**: Build complex expressions from simple, reusable building blocks
- **Market-Aware**: Native support for financial concepts like tickers, expiries, and strikes
- **Type-Safe**: Clear object types prevent common data manipulation errors

---

## Fundamental Types

### String

String literals represent text values. Strings do not require quotes and can represent tickers, month codes, and other text identifiers.

**Examples:**
```
SPX
3M
100%
DEC2026
```

### Number

Both integers and floating-point numbers are supported for numeric computations.

**Examples:**
```
100
25.5
0.75
```

### Date

Dates must follow the ISO 8601 format: `YYYY-MM-DD`

**Examples:**
```
2026-12-17
2025-06-01
2024-01-15
```

---

## Core Objects

### List

Lists are ordered collections of values, enclosed in square brackets.

**Syntax:**
```
[x1, x2, ..., xn]
```

**Examples:**
```
["SPX", "SX5E"]
[0.3, 0.7]
[1, 2, 3, 4, 5]
```

### Timeseries

A **Timeseries** is the fundamental data structure in TSIL. It represents a pandas Series object indexed by date, containing values (prices, volatilities, signals, etc.) at each point in time.

**Characteristics:**
- Indexed by date (YYYY-MM-DD)
- Can represent any numeric metric: spot prices, implied volatilities, realized volatilities, or custom signals
- Supports mathematical and statistical operations

**Example Structure:**
```
Date        Value
2025-01-01  100.5
2025-01-02  101.2
2025-01-03  99.8
...
```

---

## Instrument Objects

### Ticker (t)

A **Ticker** object represents one or more financial instruments (stocks, indices, futures contracts, etc.) identified by Bloomberg IDs or Reuters codes. Tickers can represent a single instrument or a weighted basket of instruments.

**Syntax:**
```
t(ticker_list, [weights=WGT_EQ])
```

**Parameters:**
- `ticker_list`: Single ticker string or list of ticker strings
- `weights` (optional): Weighting scheme enum or list of numeric weights. Defaults to `WGT_EQ`

**Weighting Schemes:**
- `WGT_EQ` – Equal-weighted across all instruments
- `WGT_VOL` – Volatility-weighted (inverse volatility weighting)
- `WGT_MOM` – Momentum-weighted
- `WGT_MCAP` – Market-cap weighted

**Examples:**

```python
# Single ticker
t1 = t("SPX")
t2 = t("SX5E")
t3 = t(".STOXX50E")

# Equal-weighted basket (default)
basket1 = t(["SPX", "SX5E"])
basket1 = t(["SPX", "SX5E"], WGT_EQ)  # Equivalent to above

# Custom-weighted basket
basket2 = t(["SPX", "SX5E"], [0.3, 0.7])  # SPX 30%, SX5E 70%

# Volatility-weighted basket
basket3 = t(["SPX", "SX5E", "MSFT.O"], WGT_VOL)

# Momentum-weighted basket
basket4 = t(["SPX", "SX5E"], WGT_MOM)
```

---

### Expiry (e)

An **Expiry** object specifies the maturity date or tenor for derivatives (options, futures). TSIL supports two expiry types: fixed-date expiries and constant-maturity tenors.

**Syntax:**
```
e(TENOR_OR_FIXED_EXPIRY, [DURATION_TENOR_OR_FIXED_EXPIRY])
```

**Parameters:**
- First parameter: Fixed date or tenor
- Second parameter (optional): Duration for forward expiries

#### Fixed Expiry

Fixed expiries specify a specific calendar date or contract month.

**Formats:**
- **ISO Date**: `e("2026-12-17")`
- **Month-Year**: `e("DEC2026")` or `e("DEC26")`
- **Listed Code**: `e("Z26")` (CME-style contract codes)

**Listed Monthly Expiry Codes:**
```
F = January      M = June         X = November
G = February     N = July         Z = December
H = March        Q = August
J = April        U = September
K = May          V = October
```

**Fixed Expiry Examples:**
```python
e_iso = e("2026-12-17")       # ISO date format
e_month = e("DEC2026")         # Month-Year format
e_code = e("Z26")              # Listed expiry code (December 2026)
e_short = e("JUN25")           # Short month format (June 2025)
```

#### Tenor

Tenors represent constant-maturity relative expiries. At each point in time, the metric refers to an instrument expiring at a fixed time in the future (e.g., always 3 months out).

**Tenor Format:** `{UNITS}{PERIOD}`

**Period Codes:**
- `D` – Business days
- `B` – Business days (alternative)
- `W` – Weeks
- `M` – Months
- `Y` – Years

**Tenor Examples:**
```python
e_3m = e("3M")      # 3-month tenor
e_1y = e("1Y")      # 1-year tenor
e_1w = e("1W")      # 1-week tenor
e_2d = e("2D")      # 2 business days
e_18m = e("18M")    # 18-month tenor
```

#### Forward Expiry

Forward expiries represent instruments starting at a future date and expiring after a specified duration. Use two parameters: start date and duration.

**Syntax:**
```
e(START_TENOR_OR_FIXED, DURATION_TENOR_OR_FIXED)
```

**Forward Expiry Examples:**
```python
# 1-year forward starting 6 months out (1Y6M forward)
e_fwd1 = e("1Y", "6M")

# Z contract (Dec 2026) forward 6 months
e_fwd2 = e("Z26", "6M")

# Z6 forward expiring at Z7
e_fwd3 = e("Z6", "Z7")

# 2-year forward starting 1 year out
e_fwd4 = e("1Y", "2Y")
```

---

### Strike (k)

A **Strike** object represents the exercise price for an option. Strikes can be specified as absolute prices or as relative measures (delta, moneyness, normalized levels).

**Syntax:**
```
k(FLOAT | STRIKE_STRING)
```

**Parameters:**
- `FLOAT`: Absolute strike price as a number
- `STRIKE_STRING`: Strike specification with type indicator

#### Strike Types

| Type | Indicator | Meaning | Example |
|------|-----------|---------|---------|
| Absolute | (none) | Strike price in absolute terms | `k(7500)` |
| Forward Moneyness | `%` or `%F` | Strike as % of forward price (100% = ATM) | `k("100%")` |
| Spot Moneyness | `%S` | Strike as % of spot price | `k("95%S")` |
| Delta (Auto) | `D` | Delta specification (+ for call, - for put) | `k("25D")` |
| Put Delta | `DP` | Put delta (converted to absolute) | `k("25DP")` |
| Call Delta | `DC` | Call delta (converted to absolute) | `k("25DC")` |
| Normalized | `N` | Normalized strike level | `k("1.5N")` |

#### Strike Examples

```python
# Absolute strikes
k1 = k(7500)              # 7500 absolute strike
k2 = k(100.5)             # 100.5 absolute strike

# Moneyness-based
k_atm = k("100%")         # 100% forward moneyness (at-the-money)
k_otm = k("95%")          # 95% forward moneyness (out-of-the-money)
k_spot = k("100%S")       # 100% spot moneyness

# Delta-based
k_delta_call = k("25D")   # 25 delta (interpreted as call if positive)
k_delta_put = k("-25D")   # -25 delta (put)
k_dp = k("25DP")          # 25 delta put
k_dc = k("25DC")          # 25 delta call

# Normalized
k_norm = k("1.5N")        # 1.5 normalized strike
```

---

## Metrics

**Metrics** represent specific types of timeseries data—spot prices, implied volatilities, realized volatilities, correlations, Greeks, and custom signals. Each metric is generated by applying a metric function to instrument and optional derivative parameters.

### Implied Volatility (IV)

**Implied Volatility** represents the market's expectation of future volatility, as implied by option prices. IV is a key metric for trading, risk management, and valuation.

**Syntax:**
```
IV(ticker, expiry, strike)
```

**Parameters:**
- `ticker`: Ticker object `t(...)`
- `expiry`: Expiry object `e(...)`
- `strike`: Strike object `k(...)`

**Returns:**
- A timeseries of implied volatility values indexed by date

#### Examples

**Example 1: Simple Single-Ticker IV**
```python
# SX5E (Stoxx 50 Index) 3-month ATM implied volatility
iv1 = IV(t("SX5E"), e("3M"), k("100%"))
```

**Example 2: Basket IV with Custom Weights**
```python
# Weighted average of SX5E and SPX 3-month ATM vol
# SX5E = 60% weight, SPX = 40% weight
iv2 = IV(t(["SX5E", "SPX"], [0.6, 0.4]), e("3M"), k("100%"))
```

**Example 3: Delta Call IV with Fixed Expiry**
```python
# SX5E 25 delta call on December 2026 contract
iv3 = IV(t("SX5E"), e("Z26"), k("25DC"))
```

**Example 4: Volatility-Weighted Basket IV**
```python
# Volatility-weighted basket (inverse vol weighting)
# 1-year tenor, ATM
iv4 = IV(t(["SPX", "SX5E", "MSFT.O"], WGT_VOL), e("1Y"), k("100%"))
```

**Example 5: Forward IV**
```python
# 1-year implied volatility for 6-month forward
# (Vol for contracts 1Y-6M forward)
iv5 = IV(t("SX5E"), e("1Y", "6M"), k("100%"))
```

**Example 6: Out-of-the-Money IV**
```python
# 10% out-of-the-money put IV for 3 months
iv6 = IV(t("SPX"), e("3M"), k("90%"))
```

---

## Putting It Together: Complete Workflow Examples

### Example 1: Analyzing Single Index Volatility Term Structure

```python
# Define three points on the volatility term structure for the Stoxx 50 Index
sx5e = t("SX5E")

vol_1m = IV(sx5e, e("1M"), k("100%"))   # 1-month ATM vol
vol_3m = IV(sx5e, e("3M"), k("100%"))   # 3-month ATM vol
vol_1y = IV(sx5e, e("1Y"), k("100%"))   # 1-year ATM vol

# Analyze term structure slope
term_structure_slope = vol_1y - vol_1m
```

### Example 2: Multi-Asset Basket Analysis

```python
# Create a volatility-weighted basket of major indices
basket = t(["SPX", "SX5E", ".STOXX50E", "MSFT.O"], WGT_VOL)

# Get December 2026 25 delta call IV
basket_iv = IV(basket, e("Z26"), k("25DC"))

# Compare to simple equal-weighted basket
eq_basket = t(["SPX", "SX5E", ".STOXX50E", "MSFT.O"], WGT_EQ)
eq_iv = IV(eq_basket, e("Z26"), k("25DC"))

# Difference due to weighting scheme
weighting_impact = basket_iv - eq_iv
```

### Example 3: Skew Analysis

```python
# Analyze the volatility skew (IV smile) on S&P 500 options
spx = t("SPX")

atm_vol = IV(spx, e("1M"), k("100%"))        # At-the-money
otm_put_vol = IV(spx, e("1M"), k("90%"))     # 10% OTM put
otm_call_vol = IV(spx, e("1M"), k("110%"))   # 10% OTM call

# Calculate skew
put_call_skew = otm_put_vol - otm_call_vol
```

### Example 4: Forward Vol Analysis

```python
# Analyze 1-year forward 6-month implied volatility
sx5e = t("SX5E")

# Spot 6-month vol
spot_vol_6m = IV(sx5e, e("6M"), k("100%"))

# 1-year forward 6-month vol
fwd_vol = IV(sx5e, e("1Y", "6M"), k("100%"))

# Forward premium/discount
fwd_premium = fwd_vol - spot_vol_6m
```

---

## Best Practices

1. **Use Tickers Consistently**: Stick to Bloomberg IDs or Reuters codes; don't mix conventions
2. **Chain Operations**: Build complex analyses from simple, testable components
3. **Weighting Schemes**: Understand the impact of weighting—use equal-weighting as baseline
4. **Tenor vs. Fixed Expiry**: Use tenors for rolling analysis; use fixed expiries for specific contract snapshots
5. **Strike Conventions**: Use delta conventions for options; absolute strikes for spot/forward prices

---

## Appendix: Quick Reference

| Object | Syntax | Example |
|--------|--------|---------|
| Ticker | `t(ticker)` | `t("SPX")` |
| Basket (Equal) | `t([list], WGT_EQ)` | `t(["SPX", "SX5E"])` |
| Basket (Custom) | `t([list], [weights])` | `t(["SPX", "SX5E"], [0.3, 0.7])` |
| Fixed Expiry | `e("DATE\|CODE")` | `e("Z26")` |
| Tenor | `e("TENOR")` | `e("3M")` |
| Forward Expiry | `e("START", "DUR")` | `e("1Y", "6M")` |
| Absolute Strike | `k(number)` | `k(7500)` |
| Moneyness | `k("PERCENT%")` | `k("100%")` |
| Delta | `k("DELTA[DP\|DC]")` | `k("25DC")` |
| IV | `IV(ticker, expiry, strike)` | `IV(t("SPX"), e("3M"), k("100%"))` |

