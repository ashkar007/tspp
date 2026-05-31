# TS++ Api

## Objects

### Ticker (t)

Ticker object encapsulates symbol(s). A list of tickers represents a basket. Basket is a list of tickers with a given weighting scheme. Default weighting scheme is equal (eq).
 
Syntax:  
t(ticker, weight_scheme=eq), 
where
    ticker: a single ticker (e.g SPX) or list of tickers e.g [SPX,SX5E]
    weight_scheme: weight scheme can be one of the following
        eq - equal weighted
        vol - implied vol weighted (1M atm)
        mom - momentum (macd signal)
        [] - explicit list of weights e.g [0.4,0.6]

