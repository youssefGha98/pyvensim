from __future__ import annotations

import ast
from collections.abc import Callable
from typing import Any


class ExpressionError(Exception):
    """Raised when an expression is invalid or unsafe."""


_ALLOWED_BINOPS = {
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.FloorDiv,
}

_ALLOWED_UNARYOPS = {ast.UAdd, ast.USub}

_ALLOWED_CMPOPS = {ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq}

_ALLOWED_BOOLOPS = {ast.And, ast.Or}

_ALLOWED_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.Call,
    ast.Compare,
    ast.IfExp,
    ast.BoolOp,
    # Operator nodes reached via iter_child_nodes
    *_ALLOWED_BINOPS,
    *_ALLOWED_UNARYOPS,
    *_ALLOWED_CMPOPS,
    *_ALLOWED_BOOLOPS,
}

_ALLOWED_FUNCTIONS = {"min", "max", "abs"}


def validate_expression(expression: str, params: list[str]) -> None:
    """Parse and validate an expression against the AST whitelist."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ExpressionError(f"Syntax error in expression: {e}") from e

    allowed_names = set(params) | _ALLOWED_FUNCTIONS
    _walk(tree, allowed_names)


def _walk(node: ast.AST, allowed_names: set[str]) -> None:
    """Recursively validate every AST node."""
    if type(node) not in _ALLOWED_NODES:
        raise ExpressionError(f"Disallowed syntax: {type(node).__name__}")

    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise ExpressionError(
                f"Only numeric constants allowed, got {type(node.value).__name__}"
            )

    if isinstance(node, ast.Name):
        if node.id not in allowed_names:
            raise ExpressionError(f"Unknown variable: '{node.id}'")

    if isinstance(node, ast.BinOp):
        if type(node.op) not in _ALLOWED_BINOPS:
            raise ExpressionError(
                f"Disallowed operator: {type(node.op).__name__}"
            )

    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _ALLOWED_UNARYOPS:
            raise ExpressionError(
                f"Disallowed unary operator: {type(node.op).__name__}"
            )

    if isinstance(node, ast.Compare):
        for op in node.ops:
            if type(op) not in _ALLOWED_CMPOPS:
                raise ExpressionError(
                    f"Disallowed comparison: {type(op).__name__}"
                )

    if isinstance(node, ast.BoolOp):
        if type(node.op) not in _ALLOWED_BOOLOPS:
            raise ExpressionError(
                f"Disallowed boolean operator: {type(node.op).__name__}"
            )

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ExpressionError(
                "Only simple function calls allowed (no method calls)"
            )
        if node.func.id not in _ALLOWED_FUNCTIONS:
            raise ExpressionError(f"Disallowed function: '{node.func.id}'")

    for child in ast.iter_child_nodes(node):
        _walk(child, allowed_names)


def compile_rate_function(
    expression: str, params: list[str]
) -> Callable[..., float]:
    """Validate and compile an expression string into a callable with proper signature."""
    validate_expression(expression, params)
    param_str = ", ".join(params)
    func_code = f"def _rate_func({param_str}):\n    return {expression}"
    namespace: dict[str, Any] = {"min": min, "max": max, "abs": abs}
    exec(func_code, namespace)  # noqa: S102
    return namespace["_rate_func"]
