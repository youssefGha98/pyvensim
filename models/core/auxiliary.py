from __future__ import annotations

from collections.abc import Callable

from .system_component import SystemComponent

AuxiliaryValue = Callable[[], float] | list[float] | float | None


class Auxiliary(SystemComponent):
    def __init__(self, name: str, values: AuxiliaryValue = None) -> None:
        super().__init__(name)
        self.values: AuxiliaryValue = values
        self.current_time_step: int = 0

    def value(self) -> float | None:
        if callable(self.values):
            return self.values()

        elif isinstance(self.values, list):
            if self.current_time_step < len(self.values):
                return self.values[self.current_time_step]
            else:
                return self.values[-1]

        else:
            return self.values

    def step(self, dt: float) -> None:
        self.current_time_step += 1
