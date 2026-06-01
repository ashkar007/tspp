"""
Interpreter — tree-walking evaluator for TSIL AST.

Evaluates parsed AST nodes against a symbol table populated with
TSIL built-in types, metrics, operations, and user variables.
"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from tsil.constants import WGT_EQ, WGT_MCAP, WGT_MOM, WGT_VOL
from tsil.data.mock_provider import get_default_provider
from tsil.data.provider import DataProvider
from tsil.engine.ast_nodes import (
    ASTNode,
    Assignment,
    BinaryOp,
    FunctionCall,
    Identifier,
    ListLiteral,
    NumberLiteral,
    Program,
    StringLiteral,
    UnaryOp,
)
from tsil.engine.parser import parse as parse_source
from tsil.engine.serializer import ast_to_dict, ast_to_json
from tsil.metrics.implied_vol import IV
from tsil.metrics.realised_vol import RV
from tsil.operations.functions import (
    corr,
    cov,
    diff,
    drawdown,
    mean,
    mode,
    pct_change,
    percentile,
    pow,
    sharpe,
    sqrt,
    std,
    ts_max,
    ts_min,
    ts_sum,
)
from tsil.operations.plot import plot
from tsil.types.expiry import e
from tsil.types.strike import k
from tsil.types.ticker import t
from tsil.types.timeseries import series_repr


class InterpreterError(Exception):
    """Raised when evaluation fails."""
    pass


class Engine:
    """TSIL expression engine.

    Maintains a symbol table of variables and built-in functions,
    and evaluates TSIL expressions (as strings or pre-parsed ASTs).

    Usage:
        >>> engine = Engine()
        >>> result = engine.eval('IV(t("SPX"), e("3M"), k("100%"))')

    To get the AST for REST API transport:
        >>> ast_dict = engine.parse_to_dict('IV(t("SPX"), e("3M"), k("100%"))')
    """

    def __init__(self, provider: DataProvider | None = None) -> None:
        self._provider = provider or get_default_provider()
        self._symbols: dict[str, Any] = {}
        self._init_builtins()

    def _init_builtins(self) -> None:
        """Populate symbol table with TSIL built-ins."""
        # Weight scheme constants
        self._symbols["WGT_EQ"]   = WGT_EQ
        self._symbols["WGT_VOL"]  = WGT_VOL
        self._symbols["WGT_MOM"]  = WGT_MOM
        self._symbols["WGT_MCAP"] = WGT_MCAP

        # Constructor functions
        self._symbols["t"] = t
        self._symbols["e"] = e
        self._symbols["k"] = k

        # Metric functions — inject provider
        def iv_with_provider(*args, **kwargs):
            kwargs.setdefault("provider", self._provider)
            return IV(*args, **kwargs)

        def rv_with_provider(*args, **kwargs):
            kwargs.setdefault("provider", self._provider)
            return RV(*args, **kwargs)

        self._symbols["IV"] = iv_with_provider
        self._symbols["RV"] = rv_with_provider

        # Math / stats functions
        self._symbols["sqrt"]       = sqrt
        self._symbols["diff"]       = diff
        self._symbols["pct_change"] = pct_change
        self._symbols["corr"]       = corr
        self._symbols["cov"]        = cov
        self._symbols["std"]        = std
        self._symbols["mean"]       = mean
        self._symbols["sum"]        = ts_sum
        self._symbols["min"]        = ts_min
        self._symbols["max"]        = ts_max
        self._symbols["sharpe"]     = sharpe
        self._symbols["drawdown"]   = drawdown
        self._symbols["mode"]       = mode
        self._symbols["percentile"] = percentile
        self._symbols["pow"]        = pow

        # Plotting
        self._symbols["plot"]       = plot

    # -- builtin names (for filtering user vars) ----------------------------

    _BUILTIN_NAMES = {
        "WGT_EQ", "WGT_VOL", "WGT_MOM", "WGT_MCAP",
        "t", "e", "k", "IV", "RV",
        "sqrt", "diff", "pct_change", "corr", "cov",
        "std", "mean", "sum", "min", "max",
        "sharpe", "drawdown", "mode", "percentile", "pow",
        "plot",
    }

    # -- public API ----------------------------------------------------------

    def eval(self, source: str) -> Any:
        """Parse and evaluate a TSIL expression string.

        Args:
            source: A TSIL expression or multi-statement program.

        Returns:
            The result of the last evaluated statement.
        """
        program = parse_source(source)
        return self._eval_program(program)

    def eval_ast(self, node: ASTNode) -> Any:
        """Evaluate a pre-parsed AST node."""
        return self._eval(node)

    def parse_to_dict(self, source: str) -> dict:
        """Parse a TSIL expression and return the AST as a dict.

        This is the primary mechanism for shipping a parsed TSIL query
        to a REST API endpoint for server-side evaluation.

        Args:
            source: A TSIL expression string.

        Returns:
            A JSON-serialisable dict representing the AST.
        """
        program = parse_source(source)
        return ast_to_dict(program)

    def parse_to_json(self, source: str, **json_kwargs) -> str:
        """Parse a TSIL expression and return the AST as a JSON string.

        Args:
            source: A TSIL expression string.
            **json_kwargs: Forwarded to ``json.dumps`` (e.g. ``indent=2``).

        Returns:
            A JSON string representing the AST.
        """
        program = parse_source(source)
        return ast_to_json(program, **json_kwargs)

    @property
    def variables(self) -> dict[str, Any]:
        """Currently defined user variables."""
        return {
            k: v for k, v in self._symbols.items()
            if k not in self._BUILTIN_NAMES
        }

    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable in the symbol table."""
        self._symbols[name] = value

    # -- evaluation ----------------------------------------------------------

    def _eval_program(self, program: Program) -> Any:
        result = None
        for stmt in program.statements:
            result = self._eval(stmt)
        return result

    def _eval(self, node: ASTNode) -> Any:
        if isinstance(node, NumberLiteral):
            return node.value

        if isinstance(node, StringLiteral):
            return node.value

        if isinstance(node, Identifier):
            name = node.name
            if name not in self._symbols:
                raise InterpreterError(f"Undefined variable: '{name}'")
            return self._symbols[name]

        if isinstance(node, ListLiteral):
            return [self._eval(elem) for elem in node.elements]

        if isinstance(node, FunctionCall):
            return self._eval_call(node)

        if isinstance(node, BinaryOp):
            return self._eval_binop(node)

        if isinstance(node, UnaryOp):
            return self._eval_unary(node)

        if isinstance(node, Assignment):
            value = self._eval(node.value)
            self._symbols[node.name] = value
            return value

        if isinstance(node, Program):
            return self._eval_program(node)

        raise InterpreterError(f"Unknown AST node type: {type(node).__name__}")

    def _eval_call(self, node: FunctionCall) -> Any:
        func = self._symbols.get(node.name)
        if func is None:
            raise InterpreterError(f"Undefined function: '{node.name}'")
        if not callable(func):
            raise InterpreterError(f"'{node.name}' is not callable")

        args = [self._eval(arg) for arg in node.args]
        kwargs = {k: self._eval(v) for k, v in node.kwargs.items()}

        try:
            return func(*args, **kwargs)
        except TypeError as ex:
            raise InterpreterError(
                f"Error calling {node.name}(): {ex}"
            ) from ex

    def _eval_binop(self, node: BinaryOp) -> Any:
        left = self._eval(node.left)
        right = self._eval(node.right)

        ops = {
            "+":  lambda a, b: a + b,
            "-":  lambda a, b: a - b,
            "*":  lambda a, b: a * b,
            "/":  lambda a, b: a / b,
            "**": lambda a, b: a ** b,
        }

        op_fn = ops.get(node.op)
        if op_fn is None:
            raise InterpreterError(f"Unknown operator: '{node.op}'")

        try:
            return op_fn(left, right)
        except Exception as ex:
            raise InterpreterError(
                f"Error evaluating {node.op}: {ex}"
            ) from ex

    def _eval_unary(self, node: UnaryOp) -> Any:
        operand = self._eval(node.operand)
        if node.op == "-":
            return -operand
        raise InterpreterError(f"Unknown unary operator: '{node.op}'")
