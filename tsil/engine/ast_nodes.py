"""
AST nodes for the TSIL expression language.

Every TSIL expression is parsed into a tree of these nodes, which the
interpreter then evaluates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class ASTNode:
    """Base class for all AST nodes."""
    pass


@dataclass
class NumberLiteral(ASTNode):
    """A numeric literal (int or float)."""
    value: float


@dataclass
class StringLiteral(ASTNode):
    """A string literal (double-quoted)."""
    value: str


@dataclass
class Identifier(ASTNode):
    """A name — variable reference or built-in constant."""
    name: str


@dataclass
class ListLiteral(ASTNode):
    """A list expression: [x1, x2, ..., xn]."""
    elements: list[ASTNode] = field(default_factory=list)


@dataclass
class FunctionCall(ASTNode):
    """A function or constructor call: name(arg1, arg2, ...)."""
    name: str
    args: list[ASTNode] = field(default_factory=list)
    kwargs: dict[str, ASTNode] = field(default_factory=dict)


@dataclass
class BinaryOp(ASTNode):
    """A binary operation: left op right."""
    op: str          # one of +, -, *, /, **
    left: ASTNode = field(default=None)
    right: ASTNode = field(default=None)


@dataclass
class UnaryOp(ASTNode):
    """A unary operation: -expr."""
    op: str          # currently only '-'
    operand: ASTNode = field(default=None)


@dataclass
class Assignment(ASTNode):
    """Variable assignment: name = expr."""
    name: str = ""
    value: ASTNode = field(default=None)


@dataclass
class Program(ASTNode):
    """A sequence of statements (assignments or expressions)."""
    statements: list[ASTNode] = field(default_factory=list)
