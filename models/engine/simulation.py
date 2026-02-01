from __future__ import annotations

from ..core.flow import Flow
from ..core.stock import Stock
from ..core.auxiliary import Auxiliary
from ..core.system_component import SystemComponent


class Simulation:
    def __init__(self) -> None:
        self.components: list[SystemComponent] = []
        self.history: dict[str, list[float]] = {}

    def add_component(self, component: SystemComponent) -> None:
        self.components.append(component)

    def run(self, until: float = 100, dt: float = 1) -> dict[str, list[float]]:
        time: float = 0
        self.initialize_history()
        while time < until:
            for component in self.components:
                component.step(dt)
            self.record_state(time)
            time += dt

        return self.history

    def continue_run(
        self, current_state: dict[str, float], until: float, dt: float
    ) -> dict[str, list[float]]:
        for component in self.components:
            if isinstance(component, Stock) and component.name in current_state:
                component.value = current_state[component.name]

        time = max(self.history["time"]) if self.history["time"] else 0
        while time < until:
            for component in self.components:
                component.step(dt)
            self.record_state(time)
            time += dt

        return self.history

    def initialize_history(self) -> None:
        for component in self.components:
            self.history[component.name] = []
        self.history["time"] = []

    def record_state(self, time: float) -> None:
        self.history["time"].append(time)

        for component in self.components:
            if isinstance(component, Stock):
                self.history[component.name].append(component.value)
            elif isinstance(component, Flow):
                if component.rate_function is not None:
                    self.history[component.name].append(component.rate_function())
            elif isinstance(component, Auxiliary):
                aux_value = component.value()
                if aux_value is not None:
                    self.history[component.name].append(aux_value)

    def get_results(self) -> dict[str, list[float]]:
        return self.history
