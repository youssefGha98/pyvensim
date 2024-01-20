from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario
from models.scenario.scenario_manager import ScenarioManager

from models.visualization.visualization import Visualization


auxiliaries = [
    Auxiliary("rabbit_reproduction_rate", [0.1] * 1000),  # Constant value over time
    Auxiliary(
        "hunting_rate", [0.02, 0.015, 0.01, 0.005] * 250
    ),  # Pattern repeated over time
    Auxiliary(
        "fox_reproduction_rate", [0.01]
    ),  # Constant, using a list for consistency
    Auxiliary("fox_death_rate", 0.1),  # Constant, using a float
]

# Initial values for the stocks
initial_values = {"rabbits": 100, "foxes": 20}

# Rates and rate functions for the flows
rates = {
    "rabbit_birth": {
        "rate_function": lambda rabbits, rabbit_reproduction_rate: rabbits
        * rabbit_reproduction_rate,
        "source": None,
        "destination": "rabbits",
    },
    "rabbit_death": {
        "rate_function": lambda rabbits, foxes, hunting_rate: rabbits
        * foxes
        * hunting_rate,
        "source": "rabbits",
        "destination": None,
    },
    "fox_birth": {
        "rate_function": lambda rabbits, foxes, fox_reproduction_rate: rabbits
        * foxes
        * fox_reproduction_rate,
        "source": None,
        "destination": "foxes",
    },
    "fox_death": {
        "rate_function": lambda foxes, fox_death_rate: foxes * fox_death_rate,
        "source": "foxes",
        "destination": None,
    },
}
scenario1 = Scenario("Base Scenario", {"rabbits": 100, "foxes": 20}, rates, auxiliaries)
scenario2 = Scenario("High Rabbits", {"rabbits": 200, "foxes": 20}, rates, auxiliaries)

# Add scenarios to the manager
manager = ScenarioManager()
manager.add_scenario(scenario1)
manager.add_scenario(scenario2)

# Run all scenarios
manager.run_all(simulation_time=1000, dt=1)

# Get results for a specific scenario
results = manager.get_results("Base Scenario")

# Définir la plage de valeurs pour rabbit_reproduction_rate
sensitivity_values = [0.05, 0.075, 0.1, 0.125, 0.15]

# Exécuter l'analyse de sensibilité sur le scénario 'Base Scenario'
sensitivity_results = scenario1.run_sensitivity_analysis_univariate(
    "auxiliaries", "rabbit_reproduction_rate", sensitivity_values
)

visualization = Visualization(results)
visualization.plot_sensitivity_results(
    sensitivity_results,
    stock_names=["rabbits", "foxes"],
    flow_names=["rabbit_birth", "rabbit_death"],
)
