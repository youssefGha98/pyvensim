from models.auxiliary import Auxiliary
from models.scenario import Scenario
from models.scenario_manager import ScenarioManager
import pandas as pd

# Define auxiliaries for the economic growth model
auxiliaries = [
    Auxiliary("savings_rate", [0.25] * 1000),
    Auxiliary("depreciation_rate", [0.05] * 1000),
    Auxiliary("population_growth_rate", [0.02] * 1000),
    Auxiliary("productivity", [1.0] * 1000),
]

# Initial values for the stocks
initial_values = {"capital": 100, "labor": 50, "output": 0}

# Define the rates and rate functions for the economic growth flows
rates = {
    "investment": {
        "rate_function": lambda output, savings_rate: output * savings_rate,
        "source": None,
        "destination": "capital",
    },
    "depreciation": {
        "rate_function": lambda capital, depreciation_rate: capital * depreciation_rate,
        "source": "capital",
        "destination": None,
    },
    "labor_growth": {
        "rate_function": lambda labor, population_growth_rate: labor
        * population_growth_rate,
        "source": None,
        "destination": "labor",
    },
}

# Define scenarios
scenario = Scenario("Base scenario", initial_values, rates, auxiliaries)

# Create and run the scenario
manager = ScenarioManager()
manager.add_scenario(scenario)
manager.run_all(simulation_time=1000, dt=1)

# Get and print results
results = manager.get_results("Base scenario")
print(pd.DataFrame(results))
