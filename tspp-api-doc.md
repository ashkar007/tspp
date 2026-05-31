# TS++ Api

TS++ (TimeSeries++) is a domain specific language for timeseries analysis in equity vol domain and markets in general. The primary purpose of this language is to provide an intermediary language to do such analysis with more determinism. The syntax is kept simple and succict for humans to be able to write it. However primary intention is for AI agents to take a natural language prompt and generate the TS++ script. The script would then be interpreted by TS++ runtime engine.

## Objects

### Environment (env)

Environment object hold global variables/state of the session. They must be set somewhere in the session (on the top would be best). 

#### Syntax

set_env(start_date_or_tenor, end_date, calc_missing) where
* start_date_or_tenor : explicit date or a valid tenor (see section on Tenor). Defaults to 2Y.
* end_date : (default) explicit date. Defaults to today.
* calc_missing: False

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

### Strike (stk)

Strike object represents the strike level in the implied volatility surface. It accepts an input of the form {STRIKE_LEVEL}{STRIKE_TYPE}.

Strike object can be created explicitly using 'stk' constructor. It can also be implicitly created from strings or decimal values (when the context is clear).

#### STRIKE_TYPE

Strike type gives meaning to the STRIKE_LEVEL. It can be one of the following:
1. None/Missing - absolute strike
2. F or % - forward moneyness
3. S - spot moneyness
4. D - delta. If STRIKE_LEVEL<0 then this implies Put delta and if STRIKE_LEVEL>0 then this implies Call delta
5. DP - Put Delta (STRIKE_LEVEL is converted to abs number)
6. DC - Call Delta (STRIKE_LEVEL is converted to abs number)
7. N - normalised

#### STRIKE_LEVEL

Strike level will be an decimal value thus to represent 100% user must enter 100 (rather than 0.01). Similarly for 25 delta, user must enter STRIKE_LEVEL=25.

#### Examples
1. stk(25D) or stk(25DC) : STRIKE_LEVEL=25, STRIKE_TYPE=D. Interpreted as 25DC (25 delta call)
2. stk(-15D) or stk(15DP) : STRIKE_LEVEL=-15, STRIKE_TYPE=D. Interpreted as 15DP (15 delta put)
3. stk(90%) : STRIKE_LEVEL=90, STRIKE_TYPE=F. Interpreted as 90% forward moneyness
4. stk(90.5s) : STRIKE_LEVEL=90.5, STRIKE_TYPE=S. Interpreted as 90.5% spot moneyness
5. stk(-1.5N) : STRIKE_LEVEL=-1.5, STRIKE_TYPE=N. Interpreted as -1.5 normalised strike
6. IV(SPX,3M,7300) : 7300 occurs in strike input thus is implicitly converted to stk(7300) which is 7300 absolute strike
7. IV(SPX,3M,25DC) : 25DC occurs in strike input thus is implicitly converted to stk(25DC) which is 25 delta call

## Metrics

Metrics are type of data in the timeseries for example spot price, implied volatility, realised volatility etc. 

### Implied Volatility (IV)

Option implied volatility as calibrated from market option prices. 

#### Syntax

IV(Ticker, Expiry, Strike)

#### Examples
1. IV(SX5E, 3M, 100%) : equivalent to IV(t(SX5E), e(3M), stk(100%)) - SX5E 3 month 100% (atm) vol
2. IV(t([SX5E,SPX], [0.6,0.3]), Z26, 25DC) : Average of SX5E and SPX vol on 25 delta call on December 2026 expiry. Equivalent to "0.6 * IV(SX5E, Z26, 25DC) - 0.4 * IV(SPX, Z26, 25DC)"






