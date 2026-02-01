from models.core.auxiliary import Auxiliary


class TestAuxiliary:
    def test_callable_value(self) -> None:
        aux = Auxiliary("rate", lambda: 0.5)
        assert aux.value() == 0.5

    def test_list_value_at_step_0(self) -> None:
        aux = Auxiliary("rate", [10, 20, 30])
        assert aux.value() == 10

    def test_list_value_advances_with_step(self) -> None:
        aux = Auxiliary("rate", [10, 20, 30])
        aux.step(1)
        assert aux.value() == 20

    def test_list_value_clamps_to_last(self) -> None:
        aux = Auxiliary("rate", [10, 20])
        aux.step(1)
        aux.step(1)
        aux.step(1)
        assert aux.value() == 20

    def test_scalar_value(self) -> None:
        aux = Auxiliary("rate", 3.14)
        assert aux.value() == 3.14

    def test_none_value(self) -> None:
        aux = Auxiliary("rate", None)
        assert aux.value() is None

    def test_step_increments_time_step(self) -> None:
        aux = Auxiliary("rate", [1, 2, 3])
        assert aux.current_time_step == 0
        aux.step(1)
        assert aux.current_time_step == 1
        aux.step(1)
        assert aux.current_time_step == 2
