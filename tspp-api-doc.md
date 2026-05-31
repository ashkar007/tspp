# TS++ Api

## Objects

### Ticker (t)

Ticker object encapsulates symbol(s). A list of tickers represents a basket. Basket is a list of tickers with a given weighting scheme. Default weighting scheme is equal (eq).
 
#### Syntax

t(ticker, weight_scheme=eq)
* ticker: a single ticker (e.g SPX) or list of tickers e.g [SPX,SX5E]  
* weight_scheme (optional): weight scheme can be one of the following:   
1. eq - (default) equal weighted. 
2. vol - implied vol weighted (1M atm)  
3. mom - momentum (macd signal)  
4. list of weights e.g [0.4,0.6]  

#### Examples

1. t(SPX) - single ticker
2. t([SPX,SX5E]) - basket of two tickers, equal weighted
3. t([SPX,SX5E,NKY], vol) - implied volatility weighted basket
4. t([SPX,SX5E,NKY], [0.3,0.3,0.4]) - explicit weights

### Expiry (e)

Expiry objects can be created explicitly with the 'e' constructor. Expiry object can be implicitly created from strings or date (when the context is clear). 

#### Tenor

Tenors are constant-maturity expiries i.e they are relative to a given date. Tenor has the format {unit}{period} where unit is an integer and period can be:
1. D : calendar days
2. B : business days
3. W : weeks
4. M : months
5. Y : years

#### Examples

1. 2026-12-17 or e(2026-12-17) : explicit expiry date
2. tenor or e(tenor) : see below for valid tenor




