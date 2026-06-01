import pytest
import numpy as np
import pandas as pd
from tsil.types.timeseries import make_series
from tsil.operations.functions import (
    sqrt,
    diff,
    pct_change,
    corr,
    cov,
    std,
    mean,
    ts_sum,
    ts_min,
    ts_max,
    sharpe,
    drawdown,
    mode,
    percentile,
    pow as ts_pow,
)

@pytest.fixture
def sample_series():
    dates = pd.date_range("2024-01-01", periods=10)
    raw = pd.Series([100.0, 101.0, 102.0, 101.5, 103.0, 104.0, 103.5, 105.0, 106.0, 107.0], index=dates, name="test_series")
    return make_series(raw, metric="SPOT", ticker="SPX")

@pytest.fixture
def sample_series_2():
    dates = pd.date_range("2024-01-01", periods=10)
    raw = pd.Series([10.0, 10.1, 10.2, 10.15, 10.3, 10.4, 10.35, 10.5, 10.6, 10.7], index=dates, name="test_series_2")
    return make_series(raw, metric="SPOT", ticker="SX5E")

def test_arithmetic_ops(sample_series, sample_series_2):
    # Standard pd.Series operators should work
    res_add = sample_series + sample_series_2
    assert isinstance(res_add, pd.Series)
    
    res_sub = sample_series - 10
    assert isinstance(res_sub, pd.Series)

def test_sqrt(sample_series):
    res = sqrt(sample_series)
    assert res.attrs["ticker"] == "SPX"
    assert np.allclose(res.values, np.sqrt(sample_series.values))
    assert res.name == "sqrt(test_series)"

def test_diff(sample_series):
    res = diff(sample_series, periods=2)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "diff(test_series, 2)"
    assert pd.isna(res.iloc[0])
    assert res.iloc[2] == 2.0

def test_pct_change(sample_series):
    res = pct_change(sample_series, periods=1)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "pct_change(test_series, 1)"
    assert pd.isna(res.iloc[0])
    assert np.isclose(res.iloc[1], 0.01)

def test_corr(sample_series, sample_series_2):
    res = corr(sample_series, sample_series_2, window=3)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "corr(test_series, test_series_2, 3)"
    assert pd.isna(res.iloc[1])
    assert not pd.isna(res.iloc[2])

def test_cov(sample_series, sample_series_2):
    res = cov(sample_series, sample_series_2, window=3)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "cov(test_series, test_series_2, 3)"
    assert pd.isna(res.iloc[1])
    assert not pd.isna(res.iloc[2])

def test_std(sample_series):
    res = std(sample_series, window=3)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "std(test_series, 3)"

def test_mean(sample_series):
    res = mean(sample_series, window=3)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "mean(test_series, 3)"
    assert np.isclose(res.iloc[2], 101.0)

def test_ts_sum(sample_series):
    res = ts_sum(sample_series, window=3)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "sum(test_series, 3)"
    assert res.iloc[2] == 303.0

def test_ts_min(sample_series):
    res = ts_min(sample_series, window=3)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "min(test_series, 3)"
    assert res.iloc[2] == 100.0

def test_ts_max(sample_series):
    res = ts_max(sample_series, window=3)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "max(test_series, 3)"
    assert res.iloc[2] == 102.0

def test_sharpe(sample_series):
    res = sharpe(sample_series, window=5)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "sharpe(test_series, 5)"

def test_drawdown(sample_series):
    res = drawdown(sample_series, window=5)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "drawdown(test_series, 5)"
    # At start, peak is 100.0, current is 100.0, dd is 0
    assert res.iloc[0] == 0.0

def test_mode(sample_series):
    res = mode(sample_series)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "mode(test_series)"

def test_percentile(sample_series):
    res = percentile(sample_series, 50.0)
    assert isinstance(res, float)
    # Median of [100..107] is 103.25
    assert np.isclose(res, 103.25)

def test_pow(sample_series):
    res = ts_pow(sample_series, 2)
    assert res.attrs["ticker"] == "SPX"
    assert res.name == "pow(test_series, 2)"
    assert res.iloc[0] == 10000.0
