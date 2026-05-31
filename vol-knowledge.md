# Volatility Trading

## Spot and Forward

Spot refers to current price of the underlying asset e.g SPX Index.  

Time factor (time_factor) is annualised time from today to instrument expiry.

Forward at expiry e refers to the mean of the expected terminal price distribution of an underlying asset on expiry e. It is purely a funding instrument calculated as F = Spot * (1 + exp[(-rate + dividend_yield - borrow_yield) * time_factor])

## Volatility

Volatility (vol) are of two types:

### Realised Volatility (Rz, RzVol)

Realised volatility is calculated from movements/changes in underlying security (e.g SPX Index) over N days/periods. This just requires spot prices history to calculate the timeseries of realised volatility.

There are several models:
1. C2C - (default) close-to-close price changes
2. HAR - intraday price changes, HAR-SJ model decomposes the total daily volatility into continuous and jump parts. Requires Intraday OHLCV bars.

### Implied Volatility (Imp, ImpVol)

By default Volatility should refer to Implied volatility (derived from option prices across expiries and strikes). A Vol slice refers to Imp vol at various strikes across a given expiry.

Imp vol is a function of strike (k) and expiry (e).

### At-the-money (Atm)

Atm refers to the Imp vol at a given expiry for strike=forward level, commonly represented as 100% strike in our systems.

### Out-of-the-money (Otm)

Out-of-the-money refers to strike regions on both sides of the Atm strike at-least 1 standard deviations away. In delta terms it could mean deltas smaller than 25.

### Out-of-the-money put (Otm put)

Strike regions smaller than atm strike.

### Out-of-the-money call (Otm call)

Strike regions higher than atm strike.

### Put/Call region

Put region refers to strikes lower than atm strike. Call region refers to strikes higher than atm strike.

### Skew

Consider a vol slice at a given expiry. In equities, in general, Otm puts have higher imp vol compared to Otm calls. So this creates a concave implied volatility curve tilted upwards in the put region.

Skew is calculated at Imp vol at Otm put strike - Imp vol at Otm call strike (both put and call strikes are equidistant for example 25 delta)

### Normalised skew

When atm vol is high (most probabibly due to market fear), absolute skew levels may be high too. So normalised skew divides the skew by atm vol level.






