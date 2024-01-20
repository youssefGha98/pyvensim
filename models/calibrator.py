import numpy as np
from scipy.optimize import minimize
from .stock import Stock

# ... (Autres classes) ...


class Calibrator:
    def __init__(self, scenario):
        self.scenario = scenario
        self.methods = {
            "least_squares": self._least_squares
            # Ajoutez d'autres méthodes ici si nécessaire
        }

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
        # Définition de la fonction objectif
        def objective_function(params):
            # Mettre à jour les paramètres du scenario
            self._update_scenario_params(params)
            # Exécuter la simulation
            all_simulated_data = self.scenario.run(91, 1)

            # Filtrer pour obtenir uniquement les données des stocks
            # Supposons que vous ayez une liste des noms de stocks
            stock_names = [name for name in self.scenario.initial_values.keys()]
            simulated_stock_data = {
                name: value
                for name, value in all_simulated_data.items()
                if name in stock_names
            }

            # Calculer la somme des carrés des écarts
            # Transformer simulated_stock_data en une liste ou un array
            simulated_stock_values = np.array(
                [simulated_stock_data[name] for name in stock_names]
            )
            # S'assurer que target_data est également un array NumPy
            target_data_array = [data[col].tolist() for col in data.columns]

            # Assurez-vous que data contient uniquement les données des stocks correspondants
            return np.sum((simulated_stock_values - target_data_array) ** 2)

        initial_params = self._get_initial_params()
        result = minimize(objective_function, initial_params, method="L-BFGS-B")
        return result.x  # Retourne les paramètres optimisés

    def _update_scenario_params(self, params):
        # Mettre à jour les valeurs des auxiliaries
        for i, auxiliary in enumerate(self.scenario.auxiliaries):
            auxiliary.values = params[i]

    def _get_initial_params(self):
        # Récupérer les valeurs initiales des auxiliaries
        initial_params = []
        for aux in self.scenario.auxiliaries:
            if isinstance(aux.values, list):
                # Prendre la première valeur de la liste, ou une valeur représentative
                initial_param = aux.values[0]
            else:
                # Si c'est déjà un scalaire
                initial_param = aux.values
            initial_params.append(initial_param)
        return initial_params
