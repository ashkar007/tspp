import pytest
from datetime import date
import pandas as pd
from tsil.types.ticker import t, Ticker
from tsil.types.expiry import e, Expiry
from tsil.types.strike import k, Strike
from tsil.types.timeseries import make_series, get_meta, copy_meta, series_repr
from tsil.constants import WeightScheme, StrikeType, ExpiryType

def test_ticker_single():
    tk = t("SPX")
    assert isinstance(tk, Ticker)
    assert tk.tickers == ["SPX"]
    assert not tk.is_basket
    assert tk.weight_scheme == WeightScheme.EQ
    assert tk.weights is None
    assert repr(tk) == 't("SPX")'

def test_ticker_basket_default_weights():
    tk = t(["SPX", "SX5E"])
    assert tk.tickers == ["SPX", "SX5E"]
    assert tk.is_basket
    assert tk.weight_scheme == WeightScheme.EQ
    assert tk.weights is None
    assert tk.get_equal_weights() == [0.5, 0.5]
    assert repr(tk) == "t(['SPX', 'SX5E'], WGT_EQ)"

def test_ticker_basket_scheme_weights():
    tk = t(["SPX", "SX5E"], WeightScheme.VOL)
    assert tk.weight_scheme == WeightScheme.VOL
    assert tk.weights is None
    assert repr(tk) == "t(['SPX', 'SX5E'], WGT_VOL)"

def test_ticker_basket_custom_weights():
    tk = t(["SPX", "SX5E"], [0.3, 0.7])
    assert tk.weight_scheme is None
    assert tk.weights == [0.3, 0.7]
    assert repr(tk) == "t(['SPX', 'SX5E'], [0.3, 0.7])"

def test_ticker_errors():
    with pytest.raises(ValueError, match="must not be empty"):
        t([])
    with pytest.raises(TypeError, match="Expected str or list"):
        t(123)
    with pytest.raises(ValueError, match="length.*must match"):
        t(["SPX", "SX5E"], [1.0])
    with pytest.raises(ValueError, match="must sum to 1.0"):
        t(["SPX", "SX5E"], [0.4, 0.4])
    with pytest.raises(TypeError, match="Expected WeightScheme or list"):
        t(["SPX", "SX5E"], "invalid_weight")

def test_expiry_fixed_iso():
    exp = e("2026-12-17")
    assert exp.expiry_type == ExpiryType.FIXED
    assert exp.is_fixed
    assert not exp.is_tenor
    assert not exp.is_forward
    assert exp.resolve() == date(2026, 12, 17)
    assert repr(exp) == 'e("2026-12-17")'

def test_expiry_fixed_month_year():
    exp = e("DEC2026")
    assert exp.expiry_type == ExpiryType.FIXED
    # DEC2026 third Friday: first day of month is Tuesday. First Friday is Dec 4. Third is Dec 18.
    assert exp.resolve() == date(2026, 12, 18)

def test_expiry_fixed_listed():
    exp = e("Z26")
    assert exp.expiry_type == ExpiryType.FIXED
    assert exp.resolve() == date(2026, 12, 18)

def test_expiry_tenor():
    exp = e("3M")
    assert exp.expiry_type == ExpiryType.TENOR
    assert exp.is_tenor
    as_of = date(2026, 6, 1)
    # 3M from June 1, 2026 is September 1, 2026
    assert exp.resolve(as_of) == date(2026, 9, 1)
    assert repr(exp) == 'e("3M")'

def test_expiry_forward():
    exp = e("1Y", "6M")
    assert exp.expiry_type == ExpiryType.FORWARD
    assert exp.is_forward
    as_of = date(2026, 6, 1)
    # 1Y from June 1, 2026 -> June 1, 2027. Plus 6M -> Dec 1, 2027.
    assert exp.resolve(as_of) == date(2027, 12, 1)
    assert repr(exp) == 'e("1Y", "6M")'

def test_expiry_errors():
    with pytest.raises(ValueError, match="Cannot parse expiry"):
        e("invalid_expiry")
    with pytest.raises(ValueError, match="Unknown month"):
        e("XYZ2026")

def test_strike_absolute():
    stk = k(7500)
    assert stk.strike_type == StrikeType.ABSOLUTE
    assert stk.value == 7500.0
    assert not stk.is_atm
    assert repr(stk) == "k(7500)"

def test_strike_moneyness():
    stk1 = k("100%")
    assert stk1.strike_type == StrikeType.FORWARD_MONEYNESS
    assert stk1.value == 100.0
    assert stk1.is_atm
    assert repr(stk1) == 'k("100%")'

    stk2 = k("95%S")
    assert stk2.strike_type == StrikeType.SPOT_MONEYNESS
    assert stk2.value == 95.0
    assert not stk2.is_atm
    assert repr(stk2) == 'k("95%S")'

def test_strike_delta():
    stk1 = k("25D")
    assert stk1.strike_type == StrikeType.DELTA
    assert stk1.value == 25.0

    stk2 = k("25DP")
    assert stk2.strike_type == StrikeType.DELTA_PUT
    assert stk2.value == 25.0

    stk3 = k("25DC")
    assert stk3.strike_type == StrikeType.DELTA_CALL
    assert stk3.value == 25.0

def test_strike_normalized():
    stk = k("1.5N")
    assert stk.strike_type == StrikeType.NORMALIZED
    assert stk.value == 1.5

def test_strike_errors():
    with pytest.raises(TypeError, match="Expected number or string"):
        k(None)
    with pytest.raises(ValueError, match="Cannot parse strike"):
        k("invalid_strike")

def test_timeseries_metadata():
    raw = pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2024-01-01", periods=3), name="test")
    ts = make_series(raw, metric="IV", ticker="SPX")
    assert get_meta(ts) == {"metric": "IV", "ticker": "SPX"}
    
    target = pd.Series([4.0, 5.0, 6.0], index=pd.date_range("2024-01-01", periods=3))
    copy_meta(ts, target)
    assert get_meta(target) == {"metric": "IV", "ticker": "SPX"}
    
    rep = series_repr(ts)
    assert "Timeseries(metric='IV', ticker='SPX')" in rep
