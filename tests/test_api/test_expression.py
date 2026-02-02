from __future__ import annotations

import inspect

import pytest

from api.expression import ExpressionError, compile_rate_function, validate_expression


class TestValidateExpression:
    def test_valid_arithmetic(self) -> None:
        validate_expression("a * b + c", ["a", "b", "c"])

    def test_valid_power(self) -> None:
        validate_expression("a ** 2", ["a"])

    def test_valid_ternary(self) -> None:
        validate_expression("a if b > 0 else c", ["a", "b", "c"])

    def test_valid_function_calls(self) -> None:
        validate_expression("max(a, b)", ["a", "b"])
        validate_expression("min(a, abs(b))", ["a", "b"])

    def test_valid_numeric_constant(self) -> None:
        validate_expression("a * 0.5 + 1", ["a"])

    def test_rejects_attribute_access(self) -> None:
        with pytest.raises(ExpressionError, match="Disallowed syntax"):
            validate_expression("a.__class__", ["a"])

    def test_rejects_import(self) -> None:
        with pytest.raises(ExpressionError):
            validate_expression("__import__('os')", [])

    def test_rejects_string_constant(self) -> None:
        with pytest.raises(ExpressionError, match="Only numeric constants"):
            validate_expression("'hello'", [])

    def test_rejects_undeclared_variable(self) -> None:
        with pytest.raises(ExpressionError, match="Unknown variable"):
            validate_expression("a + x", ["a"])

    def test_rejects_arbitrary_function(self) -> None:
        with pytest.raises(ExpressionError, match="Disallowed function"):
            validate_expression("eval('1')", [])

    def test_rejects_lambda(self) -> None:
        with pytest.raises(ExpressionError):
            validate_expression("(lambda: 1)()", [])

    def test_rejects_subscript(self) -> None:
        with pytest.raises(ExpressionError, match="Disallowed syntax"):
            validate_expression("a[0]", ["a"])

    def test_syntax_error(self) -> None:
        with pytest.raises(ExpressionError, match="Syntax error"):
            validate_expression("a +", ["a"])


class TestCompileRateFunction:
    def test_correct_signature(self) -> None:
        fn = compile_rate_function("a * b", ["a", "b"])
        params = list(inspect.signature(fn).parameters)
        assert params == ["a", "b"]

    def test_produces_correct_result(self) -> None:
        fn = compile_rate_function("a * b + c", ["a", "b", "c"])
        assert fn(2, 3, 4) == 10

    def test_sir_infection_rate(self) -> None:
        fn = compile_rate_function(
            "susceptible * infected * transmission_rate",
            ["susceptible", "infected", "transmission_rate"],
        )
        assert fn(50, 10, 0.015) == pytest.approx(7.5)

    def test_unary_minus(self) -> None:
        fn = compile_rate_function("-a", ["a"])
        assert fn(5) == -5

    def test_with_numeric_constant(self) -> None:
        fn = compile_rate_function("a * 2 + 1", ["a"])
        assert fn(3) == 7

    def test_ternary_expression(self) -> None:
        fn = compile_rate_function("a if a > 0 else 0", ["a"])
        assert fn(5) == 5
        assert fn(-1) == 0

    def test_safe_functions(self) -> None:
        fn = compile_rate_function("max(a, b)", ["a", "b"])
        assert fn(3, 7) == 7
