import pytest

from models.core.system_component import SystemComponent


class TestSystemComponent:
    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            SystemComponent("test")  # type: ignore[abstract]

    def test_subclass_must_implement_step(self) -> None:
        class Incomplete(SystemComponent):
            pass

        with pytest.raises(TypeError):
            Incomplete("test")  # type: ignore[abstract]

    def test_subclass_with_step_can_instantiate(self) -> None:
        class Complete(SystemComponent):
            def step(self, dt: float) -> None:
                pass

        c = Complete("test")
        assert c.name == "test"
