# Timeseries Intermediate Language (TSIL)

TSIL is a domain specific language for market timeseries analytics. It is a high level language for generating and analysing internal and market timeseries data. For example to analyse our trading risk vs SPX implied vol. The core objects in the language is timeseries (pandas Series) with meta-data (for example series name, value type, raw expression, MAIL expression).

## Objects

### String

Strings do not need to be wrapped in inverted commas for ease of use. Examples: SPX, 3M, 100%

### Number

Integers and Floats are supported.

### Date

The only acceptable format is YYYY-MM-DD

### List

Lists are repsented by [] or c(x1,x2,...,xn).

### Timeseries

Timeseries is the basic object of interaction. We use pandas.Series indexed by date to represent timeseries.

### Ticker

Tickers are strings (bloomberg id or reuters code). The position of the string parameter within a function call determines whether the string is to be treated as ticker. 

Examples: SPX, SX5E, .SPX, .STOXX50E, MSFT.O

### Basket (b)

Baskets are list of tickers with associated weighting scheme.

Syntax: b(ticker_list, weight_scheme) 
  symbol_list: list of symbols e.g [SPX,SX5E]
  weight_scheme: string (eq-equal weighted (default), vol-volatility weighted) or list of weights (e.g [0.4,0.6])

Example: 
* b([SPX,SX5E]) - equal weighted basket
* b([SPX,SX5E], eq)  - equal weighted basket
* b([SPX,SX5E], vol) - vol weighted basket

### Expiry (e)

There are two types of expiries:
* Fixed expiry date (DATE, MONTH_YEAR, LISTED_EXPIRY_CODE). These produce metrics in the timeseries where the expiries are fixed dates. 
* Tenors are constant-maturity expiries where at every point in the timeseries the metric refers to a relative expiry (e.g 1 month).

Syntax: e(TENOR_OR_FIX_EXPIRY)

Example:
* Fixed expiry - e(2026-12-17), e(Z26), e(DEC2026)
* Tenor - 3D, 2W, 18M, 2Y

#### Fixed expiry 

Monthly calendar codes are JAN,FEB,MAR,...,DEC.

Listed monthly expiry codes are F=JAN, G=FEB, H=MAR, J=APR, K=MAY, M=JUN, N=JUL, Q=AUG, U=SEP, V=OCT, X=NOV, Z=DEC

#### Tenor

Tenor format is {UNITS}{PERIOD}, where UNITS is an integer and PERIOD can be:
* D,B - business days
* W - weeks
* M - months
* Y - years

#### ForwardExpiry

Forward expiries start in the future and have a certain duration/period thus.

Format: {Start Tenor|Start Fixed Expiry}{Duration Tenor|Duration Fixed Expiry}

Example: 1Y6M, Z66M, Z6Z7

### Strike

Strike are string tokens of the 

Format: {STRIKE_LEVEL}{STRIKE_TYPE} where STRIKE_TYPE is optional.

Examples:
* 7500 - 7500 absolute strike
* 100% or 100%f - 100% forward moneyness (ATM)
* 25D - 25 delta
* 25DP, 25DC - 25 delta put and call respectively
* 1.5N - 1.5 normalised strike

#### STRIKE_TYPE

Strike type gives meaning to the STRIKE_LEVEL. It can be one of the following:
1. None/Missing - absolute strike (ABS)
2. %F or % - forward moneyness
3. %S - spot moneyness
4. D - delta. If STRIKE_LEVEL<0 then this implies Put delta and if STRIKE_LEVEL>0 then this implies Call delta
5. DP - Put Delta (STRIKE_LEVEL is converted to abs number)
6. DC - Call Delta (STRIKE_LEVEL is converted to abs number)
7. N - normalised

#### STRIKE_LEVEL

Strike level will be an decimal value.

## Metrics

Metrics are type of data in the timeseries for example spot price, implied volatility, realised volatility etc. 

### Implied Volatility (IV)

Option implied volatility as calibrated from market option prices. 

#### Syntax

IV(Ticker|Basket, Expiry, Strike)

#### Examples
1. IV(SX5E, 3M, 100%) : SX5E 3 month 100% (atm) vol
2. IV(b([SX5E,SPX], [0.6,0.3]), Z26, 25DC) : Average of SX5E and SPX vol on 25 delta call on December 2026 expiry. Equivalent to "0.6 * IV(SX5E, Z26, 25DC) - 0.4 * IV(SPX, Z26, 25DC)"
3. IV(SX5E, 1Y3M, 100%) : SX5E 1Y3M 100% (atm) forward vol
4. 





