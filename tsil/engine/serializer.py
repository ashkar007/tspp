"""
AST Serializer — converts TSIL AST to/from JSON-compatible dicts.

This enables:
  1. Sending parsed expressions to a REST API for server-side evaluation.
  2. Storing query plans / cached ASTs.
  3. Reconstructing an AST from a serialised payload.

Usage:
    from tsil.engine.serializer import ast_to_dict, dict_to_ast
    from tsil.engine.parser import parse

    tree = parse('IV(t("SPX"), e("3M"), k("100%"))')
    payload = ast_to_dict(tree)        # → JSON-serialisable dict
    restored = dict_to_ast(payload)    # → back to AST nodes
"""

from __future__ import annotations

import json
from typing import Any

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


# ---------------------------------------------------------------------------
# AST → dict
# ---------------------------------------------------------------------------

def ast_to_dict(node: ASTNode) -> dict[str, Any]:
    """Serialise an AST node tree into a JSON-compatible dictionary.

    Each node becomes a dict with a ``"type"`` key indicating the node
    class, plus the node's fields.

    Args:
        node: Root AST node.

    Returns:
        A nested dict that can be passed to ``json.dumps()``.
    """
    if isinstance(node, Program):
        return {
            "type": "Program",
            "statements": [ast_to_dict(s) for s in node.statements],
        }

    if isinstance(node, NumberLiteral):
        return {"type": "Number", "value": node.value}

    if isinstance(node, StringLiteral):
        return {"type": "String", "value": node.value}

    if isinstance(node, Identifier):
        return {"type": "Identifier", "name": node.name}

    if isinstance(node, ListLiteral):
        return {
            "type": "List",
            "elements": [ast_to_dict(e) for e in node.elements],
        }

    if isinstance(node, FunctionCall):
        result: dict[str, Any] = {
            "type": "FunctionCall",
            "name": node.name,
            "args": [ast_to_dict(a) for a in node.args],
        }
        if node.kwargs:
            result["kwargs"] = {
                k: ast_to_dict(v) for k, v in node.kwargs.items()
            }
        return result

    if isinstance(node, BinaryOp):
        return {
            "type": "BinaryOp",
            "op": node.op,
            "left": ast_to_dict(node.left),
            "right": ast_to_dict(node.right),
        }

    if isinstance(node, UnaryOp):
        return {
            "type": "UnaryOp",
            "op": node.op,
            "operand": ast_to_dict(node.operand),
        }

    if isinstance(node, Assignment):
        return {
            "type": "Assignment",
            "name": node.name,
            "value": ast_to_dict(node.value),
        }

    raise ValueError(f"Cannot serialise AST node: {type(node).__name__}")


def ast_to_json(node: ASTNode, **json_kwargs) -> str:
    """Serialise an AST node to a JSON string.

    Args:
        node:         Root AST node.
        **json_kwargs: Extra keyword arguments forwarded to ``json.dumps``
                       (e.g. ``indent=2``).

    Returns:
        A JSON string.
    """
    return json.dumps(ast_to_dict(node), **json_kwargs)


# ---------------------------------------------------------------------------
# dict → AST
# ---------------------------------------------------------------------------

_BUILDERS: dict[str, type] = {}


def dict_to_ast(d: dict[str, Any]) -> ASTNode:
    """Reconstruct an AST node tree from a serialised dictionary.

    Args:
        d: A dict previously produced by ``ast_to_dict()``.

    Returns:
        The root ASTNode.
    """
    node_type = d.get("type")
    if node_type is None:
        raise ValueError("Missing 'type' key in serialised AST dict.")

    if node_type == "Program":
        return Program(
            statements=[dict_to_ast(s) for s in d["statements"]]
        )

    if node_type == "Number":
        return NumberLiteral(value=d["value"])

    if node_type == "String":
        return StringLiteral(value=d["value"])

    if node_type == "Identifier":
        return Identifier(name=d["name"])

    if node_type == "List":
        return ListLiteral(
            elements=[dict_to_ast(e) for e in d["elements"]]
        )

    if node_type == "FunctionCall":
        kwargs = {}
        if "kwargs" in d:
            kwargs = {k: dict_to_ast(v) for k, v in d["kwargs"].items()}
        return FunctionCall(
            name=d["name"],
            args=[dict_to_ast(a) for a in d["args"]],
            kwargs=kwargs,
        )

    if node_type == "BinaryOp":
        return BinaryOp(
            op=d["op"],
            left=dict_to_ast(d["left"]),
            right=dict_to_ast(d["right"]),
        )

    if node_type == "UnaryOp":
        return UnaryOp(
            op=d["op"],
            operand=dict_to_ast(d["operand"]),
        )

    if node_type == "Assignment":
        return Assignment(
            name=d["name"],
            value=dict_to_ast(d["value"]),
        )

    raise ValueError(f"Unknown AST node type in dict: {node_type!r}")


def json_to_ast(json_str: str) -> ASTNode:
    """Reconstruct an AST from a JSON string.

    Args:
        json_str: JSON string previously produced by ``ast_to_json()``.

    Returns:
        The root ASTNode.
    """
    return dict_to_ast(json.loads(json_str))
