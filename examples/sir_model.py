from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario
from models.scenario.scenario_manager import ScenarioManager
import pandas as pd

# Define the auxiliaries for the SIR model
auxiliaries = [
    Auxiliary("transmission_rate", [0.015] * 1000),  # Beta
    Auxiliary("recovery_rate", [0.01] * 1000),  # Gamma
]

# Initial values for the stocks
initial_values = {"susceptible": 50, "infected": 10, "recovered": 0}

# Define the rates and rate functions for the SIR model flows
rates = {
    "infection": {
        "rate_function": lambda susceptible, infected, transmission_rate: susceptible
        * infected
        * transmission_rate,
        "source": "susceptible",
        "destination": "infected",
    },
    "recovery": {
        "rate_function": lambda infected, recovery_rate: infected * recovery_rate,
        "source": "infected",
        "destination": "recovered",
    },
}

# Define scenarios
scenario = Scenario("Epidemic Spread", initial_values, rates, auxiliaries)

# Create and run the scenario
manager = ScenarioManager()
manager.add_scenario(scenario)
manager.run_all(simulation_time=1000, dt=1)

# Get and print results
results = manager.get_results("Epidemic Spread")
print(pd.DataFrame(results))
