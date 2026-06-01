import pytest
import pandas as pd
from tsil import Engine, dict_to_ast, json_to_ast, ast_to_dict
from tsil.engine.interpreter import InterpreterError

def test_engine_basic_evaluation():
    engine = Engine()
    res = engine.eval('IV(t("SPX"), e("3M"), k("100%"))')
    assert isinstance(res, pd.Series)
    assert res.attrs["metric"] == "IV"
    assert res.attrs["ticker"] == 't("SPX")'

def test_engine_assignment_and_variables():
    engine = Engine()
    res = engine.eval('''
    spx = t("SPX")
    vol_3m = IV(spx, e("3M"), k("100%"))
    vol_3m_plus = vol_3m + 0.05
    vol_3m_plus
    ''')
    assert isinstance(res, pd.Series)
    assert "vol_3m" in engine.variables
    assert "spx" in engine.variables
    assert engine.eval("spx").tickers == ["SPX"]

def test_engine_builtins():
    engine = Engine()
    res = engine.eval('''
    spx = t("SPX")
    vol = IV(spx, e("3M"), k("100%"))
    mean(vol, 10)
    ''')
    assert isinstance(res, pd.Series)
    assert "mean(" in res.name

def test_engine_ast_serialization():
    engine = Engine()
    expr = 'IV(t("SPX"), e("3M"), k("100%"))'
    
    # parse_to_dict -> dict_to_ast
    ast_dict = engine.parse_to_dict(expr)
    assert isinstance(ast_dict, dict)
    assert ast_dict["type"] == "Program"
    
    ast_node = dict_to_ast(ast_dict)
    res1 = engine.eval_ast(ast_node)
    assert isinstance(res1, pd.Series)
    
    # parse_to_json -> json_to_ast
    json_str = engine.parse_to_json(expr)
    assert isinstance(json_str, str)
    
    ast_node_2 = json_to_ast(json_str)
    res2 = engine.eval_ast(ast_node_2)
    assert isinstance(res2, pd.Series)
    assert res1.equals(res2)

def test_engine_errors():
    engine = Engine()
    with pytest.raises(InterpreterError):
        engine.eval("nonexistent_var")
    with pytest.raises(InterpreterError):
        engine.eval("mean()") # Invalid arguments
