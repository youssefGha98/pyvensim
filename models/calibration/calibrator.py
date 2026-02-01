from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize

if TYPE_CHECKING:
    import pandas as pd


class Calibrator:
    def __init__(
        self,
        scenario: Any,
        simulation_time: float = 91,
        dt: float = 1,
    ) -> None:
        self.scenario = scenario
        self.simulation_time = simulation_time
        self.dt = dt
        self.methods: dict[str, Any] = {"least_squares": self._least_squares}

    def calibrate(self, data: pd.DataFrame, method: str = "least_squares") -> Any:
        if method in self.methods:
            return self.methods[method](data)
        else:
            raise ValueError(f"Method '{method}' not supported.")

    def restructure_calibration_data(
        self,
        calibration_data: NDArray[np.floating[Any]],
        num_stocks: int,
        num_data_points: int,
    ) -> NDArray[np.floating[Any]]:
        return np.reshape(calibration_data, (num_stocks, num_data_points))

    def _least_squares(self, data: pd.DataFrame) -> NDArray[np.floating[Any]]:
        def objective_function(params: NDArray[np.floating[Any]]) -> float:
            self._update_scenario_params(params)
            all_simulated_data = self.scenario.run(self.simulation_time, self.dt)

            stock_names = [name for name in self.scenario.initial_values.keys()]
            simulated_stock_data = {
                name: value
                for name, value in all_simulated_data.items()
                if name in stock_names
            }

            simulated_stock_values = np.array(
                [simulated_stock_data[name] for name in stock_names]
            )
            target_data_array = [data[col].tolist() for col in data.columns]

            return float(np.sum((simulated_stock_values - target_data_array) ** 2))

        initial_params = self._get_initial_params()
        result = minimize(objective_function, initial_params, method="L-BFGS-B")
        return result.x

    def _update_scenario_params(self, params: NDArray[np.floating[Any]]) -> None:
        for i, auxiliary in enumerate(self.scenario.auxiliaries):
            auxiliary.values = params[i]

    def _get_initial_params(self) -> list[float]:
        initial_params: list[float] = []
        for aux in self.scenario.auxiliaries:
            if isinstance(aux.values, list):
                initial_param = aux.values[0]
            else:
                initial_param = aux.values
            initial_params.append(initial_param)
        return initial_params
