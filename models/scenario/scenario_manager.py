from __future__ import annotations

from .scenario import Scenario


class ScenarioManager:
    def __init__(self) -> None:
        self.scenarios: list[Scenario] = []

    def add_scenario(self, scenario: Scenario) -> None:
        self.scenarios.append(scenario)

    def reset_timesteps(self, scenario: Scenario) -> None:
        for aux in scenario.auxiliaries:
            aux.current_time_step = 0

    def run_all(self, simulation_time: float, dt: float) -> None:
        for scenario in self.scenarios:
            self.reset_timesteps(scenario)
            scenario.run(simulation_time, dt)

    def get_results(self, scenario_name: str) -> dict[str, list[float]] | None:
        for scenario in self.scenarios:
            if scenario.name == scenario_name:
                return scenario.results
        return None
