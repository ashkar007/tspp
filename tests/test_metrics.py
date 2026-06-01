import pytest
from datetime import date
import pandas as pd
from tsil import t, e, k, IV, RV
from tsil.constants import WeightScheme
from tsil.data.mock_provider import get_default_provider

def test_single_ticker_iv():
    provider = get_default_provider()
    res = IV(t("SPX"), e("3M"), k("100%"), provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["metric"] == "IV"
    assert res.attrs["ticker"] == 't("SPX")'
    assert res.attrs["expiry"] == 'e("3M")'
    assert res.attrs["strike"] == 'k("100%")'
    assert not res.empty
    assert res.name == "IV:SPX:3M:100%"

def test_basket_ticker_iv_equal_weight():
    provider = get_default_provider()
    res = IV(t(["SPX", "SX5E"], WeightScheme.EQ), e("3M"), k("100%"), provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["metric"] == "IV"
    assert res.attrs["ticker"] == "t(['SPX', 'SX5E'], WGT_EQ)"
    assert res.name == "IV:basket:3M:100%"

def test_basket_ticker_iv_custom_weight():
    provider = get_default_provider()
    res = IV(t(["SPX", "SX5E"], [0.4, 0.6]), e("3M"), k("100%"), provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["ticker"] == "t(['SPX', 'SX5E'], [0.4, 0.6])"

def test_basket_ticker_iv_vol_weight():
    provider = get_default_provider()
    res = IV(t(["SPX", "SX5E"], WeightScheme.VOL), e("3M"), k("100%"), provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["ticker"] == "t(['SPX', 'SX5E'], WGT_VOL)"

def test_basket_ticker_iv_mom_weight():
    provider = get_default_provider()
    res = IV(t(["SPX", "SX5E"], WeightScheme.MOM), e("3M"), k("100%"), provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["ticker"] == "t(['SPX', 'SX5E'], WGT_MOM)"

def test_basket_ticker_iv_mcap_weight():
    provider = get_default_provider()
    res = IV(t(["SPX", "SX5E"], WeightScheme.MCAP), e("3M"), k("100%"), provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["ticker"] == "t(['SPX', 'SX5E'], WGT_MCAP)"

def test_single_ticker_rv():
    provider = get_default_provider()
    res = RV(t("SPX"), window=30, provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["metric"] == "RV"
    assert res.attrs["ticker"] == 't("SPX")'
    assert res.attrs["window"] == 30
    assert not res.empty
    assert res.name == "RV:SPX:30d"

def test_basket_ticker_rv():
    provider = get_default_provider()
    res = RV(t(["SPX", "SX5E"]), window=30, provider=provider)
    assert isinstance(res, pd.Series)
    assert res.attrs["metric"] == "RV"
    assert res.attrs["ticker"] == "t(['SPX', 'SX5E'], WGT_EQ)"
    assert res.attrs["window"] == 30
    assert not res.empty
    assert res.name == "RV:basket:30d"
