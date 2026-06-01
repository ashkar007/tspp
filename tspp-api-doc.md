# Timeseries Intermediate Language (TSIL)

TSIL is a domain specific language for market timeseries analytics. It is a high level language for generating and analysing signals and market timeseries data. For example to analyse correlation of US CPI vs SPX implied vol. The core objects in the language is timeseries (pandas DataFrame).

## Fundamental Types

### String

Strings : "SPX", "3M", "100%"

### Number

Integers and Floats are supported.

### Date

The only acceptable format is YYYY-MM-DD

## Objects

### List

Lists are repsented by [x1,x2,...,xn]

### Timeseries

Timeseries (pandas Series) is the main object of computation. We use pandas.Series indexed by date to represent timeseries.

### Ticker (t)

Tickers are created by t(). Tickers can be a single symbol (bloomberg id or reuters code) or a list of symbols with weights (basket). If a list is passed in but no weights, weights default to equal weighted. 

Syntax: t(ticker_list, weights=WGT_EQ)
  ticker_list: can be single string or list of strings
  weights: weights enum or list of weights (floats)

Examples:
* t1 = t("SPX")
* t2 = t(".STOXX50E")
* basket = t(["SPX",".STOXX50E"]); // equal weighted basket
* basket = t(["SPX",".STOXX50E"], [0.3,0.7]); // SPX = 30%, .STOXX50E = 70%
* basket = t(["SPX",".STOXX50E"], WGT_VOL); // equal weighted basket

Weights enum:
* WGT_EQ
* WGT_VOL
* WGT_MOM
* WGT_MCAP

### Expiry (e)

There are two types of expiries:
* Fixed expiry date can be DATE or MONTH_YEAR, LISTED_EXPIRY_CODE. These produce metrics in the timeseries where the expiries are fixed dates. 
* Tenors are constant-maturity expiries where at every point in the timeseries the metric refers to a relative expiry (e.g 1 month).

Syntax: e(TENOR_OR_FIXED_EXPIRY, [DURATION TENOR_OR_FIXED_EXPIRY])

Example:
* Fixed expiry - e("2026-12-17"), e("Z26"), e("DEC2026")
* Tenor - e("3D"), e("2W"), e("18M"), e("2Y")
* Forward expiry - e("1Y", "6M")

#### Fixed expiry 

MONTH_YEAR: format {MMM}{YY}. Months are JAN,FEB,MAR,...,DEC e.g DEC26 for December 2026

LISTED_EXPIRY_CODE: format {LISTED_MONTH_CODE}{YY}. Listed monthly expiry codes are F=JAN, G=FEB, H=MAR, J=APR, K=MAY, M=JUN, N=JUL, Q=AUG, U=SEP, V=OCT, X=NOV, Z=DEC. e.g. Z26.

#### Tenor

Tenor format is {UNITS}{PERIOD}, where UNITS is an integer and PERIOD can be:
* D,B - business days
* W - weeks
* M - months
* Y - years

#### ForwardExpiry

Forward expiries start in the future and have a certain duration/period thus. This is created by passing second argument in 'e' constructor.

Example: e("1Y", "6M"), e("Z6","6M"), e("Z6","Z7")

### Strike (k)

Strike may be created from a number (absolute strike) or a STRIKE_STRING of the format {STRIKE_LEVEL}{STRIKE_TYPE}. See strike types below.

Syntax: k(FLOAT|STRIKE_STRING)

#### STRIKE_TYPE

Strike type gives meaning to the STRIKE_LEVEL. It can be one of the following:
1. % - forward moneyness
2. %S - spot moneyness
3. D - delta. If STRIKE_LEVEL<0 then this implies Put delta and if STRIKE_LEVEL>0 then this implies Call delta
4. DP - Put Delta (STRIKE_LEVEL is converted to abs number)
5. DC - Call Delta (STRIKE_LEVEL is converted to abs number)
6. N - normalised

#### Examples
* 7500 - 7500 absolute strike
* 100% or 100%f - 100% forward moneyness (ATM)
* 25D - 25 delta
* 25DP, 25DC - 25 delta put and call respectively
* 1.5N - 1.5 normalised strike

#### STRIKE_LEVEL

Strike level will be an int or float value.

## Metrics

Metrics are type of data in the timeseries for example spot price, implied volatility, realised volatility etc. 

### Implied Volatility (IV)

Option implied volatility as calibrated from market option prices. 

#### Syntax

IV(Ticker, Expiry, Strike)

#### Examples
1. t1 = IV(t("SX5E"), e("3M"), k("100%")) : SX5E 3 month 100% (atm) vol
2. t2 = IV(t(["SX5E","SPX"], [0.6,0.3]), e("Z26"), k("25DC")) : Average of SX5E and SPX vol on 25 delta call on December 2026 expiry.
3. t3 = IV(t("SX5E"), e("1Y3M"), k("100%")) : SX5E 1Y3M 100% (atm) forward vol






