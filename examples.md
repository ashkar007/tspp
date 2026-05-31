# TS++ examples

## Basket

Syntax: b(ticker_list, weight_scheme)

x1 = b([spx, sx5e]); // default weight scheme and weights  
x2 = b([spx, sx5e], wvol) // weighted by realised vol levels.  
x3 = b([spx, sx5e], [0.4,0.6]) // custom weights. 


