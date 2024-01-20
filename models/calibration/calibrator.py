import numpy as np
from scipy.optimize import minimize


class Calibrator:
    def __init__(self, scenario):
        self.scenario = scenario
        self.methods = {"least_squares": self._least_squares}

    def calibrate(self, data, method="least_squares"):
        if method in self.methods:
            return self.methods[method](data)
        else:
            raise ValueError(f"Method '{method}' not supported.")

    def restructure_calibration_data(
        self, calibration_data, num_stocks, num_data_points
    ):
        return np.reshape(calibration_data, (num_stocks, num_data_points))

    def _least_squares(self, data):
        def objective_function(params):
            self._update_scenario_params(params)
            all_simulated_data = self.scenario.run(91, 1)

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

            return np.sum((simulated_stock_values - target_data_array) ** 2)

        initial_params = self._get_initial_params()
        result = minimize(objective_function, initial_params, method="L-BFGS-B")
        return result.x

    def _update_scenario_params(self, params):
        for i, auxiliary in enumerate(self.scenario.auxiliaries):
            auxiliary.values = params[i]

    def _get_initial_params(self):
        initial_params = []
        for aux in self.scenario.auxiliaries:
            if isinstance(aux.values, list):
                initial_param = aux.values[0]
            else:
                initial_param = aux.values
            initial_params.append(initial_param)
        return initial_params
