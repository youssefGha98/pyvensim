from .stock import Stock
from .flow import Flow
from .simulation import Simulation
from .auxiliary import Auxiliary
from .calibrator import Calibrator
import pandas as pd


class Scenario:
    def __init__(self, name, initial_values, rates, auxiliaries):
        self.name = name
        self.initial_values = initial_values
        self.rates = rates
        self.auxiliaries = auxiliaries
        self.results = None

    def construct_simulation(self, modified_parameters=None):
        # Create stocks
        stocks = {
            name: Stock(name, initial_value)
            for name, initial_value in self.initial_values.items()
        }

        # Apply any modifications to initial values if provided
        if modified_parameters and "initial_values" in modified_parameters:
            for name, value in modified_parameters["initial_values"].items():
                if name in stocks:
                    stocks[name].value = value

        # Create auxiliaries as a dictionary
        aux_values = {aux.name: aux.value() for aux in self.auxiliaries}

        # Create flows with a lambda that captures the current state of stocks and auxiliaries
        flows = []
        for rate_name, rate_details in self.rates.items():
            rate_function = rate_details["rate_function"]
            source = rate_details.get("source")
            destination = rate_details.get("destination")

            # Update the rate function to use the current values from stocks and auxiliaries
            wrapped_rate_function = (  # noqa: E731
                lambda s=stocks, a=aux_values, rf=rate_function: rf(
                    **{
                        key: s[key].value if key in s else a[key]
                        for key in rf.__code__.co_varnames
                    }
                )
            )

            source_stock = stocks.get(source) if source else None
            destination_stock = stocks.get(destination) if destination else None
            flow = Flow(
                rate_name, source_stock, destination_stock, wrapped_rate_function
            )
            flows.append(flow)

        # Create the simulation
        simulation = Simulation()
        for stock in stocks.values():
            simulation.add_component(stock)
        for flow in flows:
            simulation.add_component(flow)
        for auxiliary in self.auxiliaries:
            simulation.add_component(auxiliary)

        return simulation

    def run(self, simulation_time, dt):
        simulation = self.construct_simulation()
        self.results = simulation.run(until=simulation_time, dt=dt)
        return self.results

    def run_sensitivity_analysis_univariate(
        self, component_name, parameter, range_values, until=100, dt=1
    ):
        original_values = self._get_original_values(component_name, parameter)
        results = {}

        for value in range_values:
            self._modify_component_value(component_name, parameter, value)
            simulation = self.construct_simulation()
            results[value] = simulation.run(until, dt)
            self._restore_original_values(component_name, parameter, original_values)

        return results

    def run_sensitivity_analysis_multivariate(
        self, parameters, param_combinations, until=100, dt=1
    ):
        results = {}
        original_values = {}

        # Enregistrer toutes les valeurs originales avant de commencer les simulations
        for param in parameters:
            original_values[param["name"]] = self._get_original_values(
                param["component"], param["name"]
            )

        for combination in param_combinations:
            # Appliquer la combinaison des paramètres à la simulation
            for i, param in enumerate(parameters):
                self._modify_component_value(
                    param["component"], param["name"], combination[i]
                )

            # Exécuter la simulation avec la combinaison de paramètres actuelle
            simulation = self.construct_simulation()
            results[combination] = simulation.run(until, dt)

            # Restaurer les valeurs originales après chaque simulation
            for param in parameters:
                self._restore_original_values(
                    param["component"], param["name"], original_values[param["name"]]
                )

        return results

    def _get_original_values(self, component_name, parameter):
        # Ici, récupérez et renvoyez les valeurs originales du composant spécifié
        if component_name == "auxiliaries":
            for aux in self.auxiliaries:
                if aux.name == parameter:
                    return aux.values
        elif component_name == "stocks":
            return self.initial_values[parameter]
        # Ajoutez une logique similaire pour 'flows' si nécessaire

    def _modify_component_value(self, component_name, parameter, value):
        # Ici, modifiez la valeur du composant spécifié
        if component_name == "auxiliaries":
            for aux in self.auxiliaries:
                if aux.name == parameter:
                    aux.values = value
        elif component_name == "stocks":
            self.initial_values[parameter] = value
        # Ajoutez une logique similaire pour 'flows' si nécessaire

    def _restore_original_values(self, component_name, parameter, original_values):
        # Ici, restaurez les valeurs originales du composant spécifié
        if component_name == "auxiliaries":
            for aux in self.auxiliaries:
                if aux.name == parameter:
                    aux.values = original_values
        elif component_name == "stocks":
            self.initial_values[parameter] = original_values
        # Ajoutez une logique similaire pour 'flows' si nécessaire

    def calculate_elasticities(
        self, sensitivity_results, base_params, comparison_params, stock_name
    ):
        elasticities = {}
        base_df = pd.DataFrame(sensitivity_results[base_params])
        base_population = base_df[
            stock_name
        ].mean()  # Ou une autre mesure centrale selon le contexte

        for params, comparison_dict in sensitivity_results.items():
            if params != base_params:
                comparison_df = pd.DataFrame(comparison_dict)
                comparison_population = comparison_df[stock_name].mean()  # Idem
                percentage_change_in_population = (
                    (comparison_population - base_population) / base_population
                ) * 100
                percentage_change_in_params = (
                    (params[0] - base_params[0]) / base_params[0]
                ) * 100  # Adapté pour un seul paramètre, à généraliser si nécessaire

                if percentage_change_in_params != 0:
                    elasticity = (
                        percentage_change_in_population / percentage_change_in_params
                    )
                    elasticities[params] = elasticity

        return elasticities

    def apply_shock_over_period(self, components, until=100, dt=1):
        original_values = {}

        # Appliquer le choc
        for component_name, details in components.items():
            component_type = details["component_type"]
            shock_value = details["shock_value"]
            start_time = details["start_time"]
            end_time = details["end_time"]
            if end_time <= start_time:
                raise ValueError(
                    f"end_time must be greater than start_time for {component_name}"
                )

            if component_type == "auxiliary":
                for i, aux in enumerate(self.auxiliaries):
                    if aux.name == component_name:
                        original_values[component_name] = list(aux.values)
                        pre_shock_values = original_values[component_name][:start_time]
                        shock_period_values = [shock_value] * (end_time - start_time)
                        post_shock_values = original_values[component_name][end_time:]

                        self.auxiliaries[i].values = (
                            pre_shock_values + shock_period_values + post_shock_values
                        )

            elif component_type == "stock":
                for stock in self.stocks:
                    if stock.name == component_name:
                        original_values[component_name] = stock.value
                        stock.value = shock_value

            elif component_type == "flow":
                for flow in self.flows:
                    if flow.name == component_name:
                        original_values[component_name] = flow.rate_function
                        flow.rate_function = lambda: shock_value

        # Exécuter la simulation
        self.run(until, dt)
        # Restaurer les valeurs originales
        for component_name, details in components.items():
            component_type = details["component_type"]
            if component_type == "auxiliary":
                for i, aux in enumerate(self.auxiliaries):
                    if aux.name == component_name:
                        self.auxiliaries[i].values = original_values[component_name]
            elif component_type == "stock":
                self.stocks[component_name].value = original_values[component_name]
            elif component_type == "flow":
                self.flows[component_name].rate_function = original_values[
                    component_name
                ]

    def calibrate(self, data, method="least_squares"):
        calibrator = Calibrator(self)
        calibrator.calibrate(data, method)
