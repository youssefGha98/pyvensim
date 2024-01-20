from .flow import Flow
from .stock import Stock
from .auxiliary import Auxiliary


class Simulation:
    def __init__(self):
        self.components = []
        self.history = {}  # Changed to a dictionary

    def add_component(self, component):
        self.components.append(component)

    def run(self, until=100, dt=1):
        time = 0
        self.initialize_history()  # Initialize history with keys
        while time < until:
            for component in self.components:
                component.step(dt)
            self.record_state(time)
            time += dt

        return self.history  # Return the modified history structure

    def continue_run(self, current_state, until, dt):
        # Configure l'état initial de la simulation avec les valeurs actuelles
        for component in self.components:
            if isinstance(component, Stock) and component.name in current_state:
                component.value = current_state[component.name]

        # Continue la simulation à partir de l'état actuel
        time = max(self.history["time"]) if self.history["time"] else 0
        while time < until:
            for component in self.components:
                component.step(dt)
            self.record_state(time)
            time += dt

        return self.history

    def initialize_history(self):
        # Initialize the history dictionary with keys for each component and time
        for component in self.components:
            self.history[component.name] = []
        self.history["time"] = []

    def record_state(self, time):
        # Add the current time to the history
        self.history["time"].append(time)

        # Record the state of each stock
        for component in self.components:
            if isinstance(component, Stock):
                self.history[component.name].append(component.value)
            elif isinstance(component, Flow):
                self.history[component.name].append(component.rate_function())
            elif isinstance(component, Auxiliary):
                aux_value = component.value()
                self.history[component.name].append(aux_value)

    def get_results(self):
        return self.history
