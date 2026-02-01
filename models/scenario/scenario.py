from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

import pandas as pd

from ..calibration.calibrator import Calibrator
from ..core.auxiliary import Auxiliary
from ..core.flow import Flow
from ..core.stock import Stock
from ..engine.simulation import Simulation


class Scenario:
    def __init__(
        self,
        name: str,
        initial_values: dict[str, float],
        rates: dict[str, dict[str, Any]],
        auxiliaries: list[Auxiliary],
    ) -> None:
        self.name = name
        self.initial_values = initial_values
        self.rates = rates
        self.auxiliaries = auxiliaries
        self.results: dict[str, list[float]] | None = None

    def construct_simulation(
        self, modified_parameters: dict[str, Any] | None = None
    ) -> Simulation:
        stocks = {
            name: Stock(name, initial_value)
            for name, initial_value in self.initial_values.items()
        }

        if modified_parameters and "initial_values" in modified_parameters:
            for name, value in modified_parameters["initial_values"].items():
                if name in stocks:
                    stocks[name].value = value

        aux_values = {aux.name: aux.value() for aux in self.auxiliaries}

        flows: list[Flow] = []
        for rate_name, rate_details in self.rates.items():
            rate_function: Callable[..., float] = rate_details["rate_function"]
            source: str | None = rate_details.get("source")
            destination: str | None = rate_details.get("destination")

            params = list(inspect.signature(rate_function).parameters)

            wrapped_rate_function = (  # noqa: E731
                lambda s=stocks, a=aux_values, rf=rate_function, p=params: rf(
                    **{
                        key: s[key].value if key in s else a[key]
                        for key in p
                    }
                )
            )

            source_stock = stocks.get(source) if source else None
            destination_stock = stocks.get(destination) if destination else None
            flow = Flow(
                rate_name, source_stock, destination_stock, wrapped_rate_function
            )
            flows.append(flow)

        simulation = Simulation()
        for stock in stocks.values():
            simulation.add_component(stock)
        for flow in flows:
            simulation.add_component(flow)
        for auxiliary in self.auxiliaries:
            simulation.add_component(auxiliary)

        return simulation

    def run(self, simulation_time: float, dt: float) -> dict[str, list[float]]:
        simulation = self.construct_simulation()
        self.results = simulation.run(until=simulation_time, dt=dt)
        return self.results

    def run_sensitivity_analysis_univariate(
        self,
        component_name: str,
        parameter: str,
        range_values: list[Any],
        until: float = 100,
        dt: float = 1,
    ) -> dict[Any, dict[str, list[float]]]:
        original_values = self._get_original_values(component_name, parameter)
        results: dict[Any, dict[str, list[float]]] = {}

        for value in range_values:
            self._modify_component_value(component_name, parameter, value)
            simulation = self.construct_simulation()
            results[value] = simulation.run(until, dt)
            self._restore_original_values(component_name, parameter, original_values)

        return results

    def run_sensitivity_analysis_multivariate(
        self,
        parameters: list[dict[str, str]],
        param_combinations: list[tuple[Any, ...]],
        until: float = 100,
        dt: float = 1,
    ) -> dict[tuple[Any, ...], dict[str, list[float]]]:
        results: dict[tuple[Any, ...], dict[str, list[float]]] = {}
        original_values: dict[str, Any] = {}

        for param in parameters:
            original_values[param["name"]] = self._get_original_values(
                param["component"], param["name"]
            )

        for combination in param_combinations:
            for i, param in enumerate(parameters):
                self._modify_component_value(
                    param["component"], param["name"], combination[i]
                )

            simulation = self.construct_simulation()
            results[combination] = simulation.run(until, dt)

            for param in parameters:
                self._restore_original_values(
                    param["component"], param["name"], original_values[param["name"]]
                )

        return results

    def _get_original_values(self, component_name: str, parameter: str) -> Any:
        if component_name == "auxiliaries":
            for aux in self.auxiliaries:
                if aux.name == parameter:
                    return aux.values
        elif component_name == "stocks":
            return self.initial_values[parameter]
        return None

    def _modify_component_value(
        self, component_name: str, parameter: str, value: Any
    ) -> None:
        if component_name == "auxiliaries":
            for aux in self.auxiliaries:
                if aux.name == parameter:
                    aux.values = value
        elif component_name == "stocks":
            self.initial_values[parameter] = value

    def _restore_original_values(
        self, component_name: str, parameter: str, original_values: Any
    ) -> None:
        if component_name == "auxiliaries":
            for aux in self.auxiliaries:
                if aux.name == parameter:
                    aux.values = original_values
        elif component_name == "stocks":
            self.initial_values[parameter] = original_values

    def calculate_elasticities(
        self,
        sensitivity_results: dict[tuple[Any, ...], dict[str, list[float]]],
        base_params: tuple[Any, ...],
        comparison_params: tuple[Any, ...],
        stock_name: str,
    ) -> dict[tuple[Any, ...], float]:
        elasticities: dict[tuple[Any, ...], float] = {}
        base_df = pd.DataFrame(sensitivity_results[base_params])
        base_population: float = base_df[stock_name].mean()

        for params, comparison_dict in sensitivity_results.items():
            if params != base_params:
                comparison_df = pd.DataFrame(comparison_dict)
                comparison_population: float = comparison_df[stock_name].mean()
                percentage_change_in_population = (
                    (comparison_population - base_population) / base_population
                ) * 100
                percentage_change_in_params = (
                    (params[0] - base_params[0]) / base_params[0]
                ) * 100

                if percentage_change_in_params != 0:
                    elasticity = (
                        percentage_change_in_population / percentage_change_in_params
                    )
                    elasticities[params] = elasticity

        return elasticities

    def apply_shock_over_period(
        self, components: dict[str, dict[str, Any]], until: float = 100, dt: float = 1
    ) -> None:
        original_values: dict[str, Any] = {}

        # Apply the shock
        for component_name, details in components.items():
            component_type: str = details["component_type"]
            shock_value: float = details["shock_value"]
            start_time: int = details["start_time"]
            end_time: int = details["end_time"]
            if end_time <= start_time:
                raise ValueError(
                    f"end_time must be greater than start_time for {component_name}"
                )

            if component_type == "auxiliary":
                for i, aux in enumerate(self.auxiliaries):
                    if aux.name == component_name:
                        original_values[component_name] = list(aux.values)  # type: ignore[arg-type]
                        pre_shock_values = original_values[component_name][:start_time]
                        shock_period_values = [shock_value] * (end_time - start_time)
                        post_shock_values = original_values[component_name][end_time:]

                        self.auxiliaries[i].values = (
                            pre_shock_values + shock_period_values + post_shock_values
                        )

            elif component_type == "stock":
                if component_name in self.initial_values:
                    original_values[component_name] = self.initial_values[component_name]
                    self.initial_values[component_name] = shock_value

            elif component_type == "flow":
                if component_name in self.rates:
                    original_values[component_name] = self.rates[component_name]["rate_function"]
                    sv = shock_value  # capture by value
                    self.rates[component_name]["rate_function"] = lambda sv=sv: sv  # noqa: E731

        self.run(until, dt)

        # Restore original values
        for component_name, details in components.items():
            component_type = details["component_type"]
            if component_type == "auxiliary":
                for i, aux in enumerate(self.auxiliaries):
                    if aux.name == component_name:
                        self.auxiliaries[i].values = original_values[component_name]
            elif component_type == "stock":
                if component_name in self.initial_values:
                    self.initial_values[component_name] = original_values[component_name]
            elif component_type == "flow":
                if component_name in self.rates:
                    self.rates[component_name]["rate_function"] = original_values[
                        component_name
                    ]

    def calibrate(
        self,
        data: pd.DataFrame,
        method: str = "least_squares",
        simulation_time: float = 91,
        dt: float = 1,
    ) -> Any:
        calibrator = Calibrator(self, simulation_time=simulation_time, dt=dt)
        return calibrator.calibrate(data, method)
