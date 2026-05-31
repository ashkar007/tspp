# TS++ Api

TS++ is a domain specific language for relative-value analysis in equity vol domain and financial markets in general. The primary purpose is for AI agent  to translate natural language prompts into TS++ code for evaluation. However I have kept the syntax flexible and less verbose so that expert users can directly write the expressions themselves.  

## Objects

### Ticker (t)

Ticker object encapsulates symbol(s). A list of tickers with a weight scheme represents a basket. A single ticker can be thought of as a basket of 1 ticker with 100% weight. Ticker object can be implicitly created from strings or list of strings when the context is clear.
 
#### Syntax

t(ticker, weight_scheme=eq) where
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
4. t([SPX,SX5E,NKY], [0.3,0.3,0.4]) - explicit weights SPX 30%, SX5E 30%, NKY 40%
5. IV(SPX,3M,100) - SPX is implicitly promoted to t(SPX) because the first parameter of IV function is ticker and SPX is a valid ticker.

### Expiry (e)

Expiry objects can represent few things commonly encountered trading vol:
1. Straight-forward expiry date (e.g 2026-12-17)
2. Expiry code (e.g DEC26,DEC2026,Z26,Z2026 all refer to standard monthly December 2026 expiry)
3. Tenor (e.g 3M, 2Y, described in more detail below)
4. Forward Vol (requires a start expiry and end expiry)

Expiry objects can be created explicitly with the 'e' constructor. Expiry object can be implicitly created from strings or date (when the context is clear). For the sake of having clear grammar we will split the type of Expiries into:
1. EXPIRY_DATE_CODE - 
2. TENOR - Creates a constant maturity expiry in the timeseries (on each date the expiry date will have same vollife e.g 1 month).

#### EXPIRY_DATE_CODE
Could be an explicit EXPIRYDATE or an EXPIRYCODE. Both create a fixed expiry date in the timeseries.
1. EXPIRYDATE - format YYYY-mm-dd (e.g 2026-12-17)
2. EXPIRYCODE - format MMMYY or {MONTHCODE}YY (e.g DEC26 or Z26)
Valid MONTHCODE are F=JAN,=FEB,H=MAR,=APR,=MAY,M=JUN,=JUL,=AUG,U=SEP,=OCT,=NOV,Z=DEC

#### TENOR

Tenors are constant-maturity expiries i.e they are relative to a given date. Tenor has the format {unit}{period} where unit is an integer and period can be:
1. D : calendar days
2. B : business days
3. W : weeks
4. M : months
5. Y : years
Examples: 5B - 5 business days, 1W - 1 week, 3M - 3 months, 5Y - 5 years





