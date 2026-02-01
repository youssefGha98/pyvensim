import pytest

from models.core.stock import Stock


class TestStock:
    def test_initial_value_default(self) -> None:
        s = Stock("x")
        assert s.value == 0

    def test_initial_value_custom(self) -> None:
        s = Stock("x", initial_value=42)
        assert s.value == 42

    def test_change_positive(self) -> None:
        s = Stock("x", 10)
        s.change(5)
        assert s.value == 15

    def test_change_negative(self) -> None:
        s = Stock("x", 10)
        s.change(-3)
        assert s.value == 7

    def test_change_raises_on_inf(self) -> None:
        s = Stock("x", 0)
        with pytest.raises(ValueError, match="non-finite"):
            s.change(float("inf"))

    def test_change_raises_on_nan(self) -> None:
        s = Stock("x", 0)
        with pytest.raises(ValueError, match="non-finite"):
            s.change(float("nan"))

    def test_step_does_not_change_value(self) -> None:
        s = Stock("x", 10)
        s.step(1)
        assert s.value == 10
