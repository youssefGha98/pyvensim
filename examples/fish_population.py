import pandas as pd
import math
import random

from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario
from models.scenario.scenario_manager import ScenarioManager

simulation_time = 1000


# Example of auxiliaries as functions returning lists
def generate_temperature_series(timesteps, base_temp, amplitude, phase_shift):
    # Simulate daily temperature changes or seasonal if timesteps are in days
    return [
        base_temp + amplitude * math.sin((2 * math.pi / timesteps) * t + phase_shift)
        for t in range(timesteps)
    ]


def generate_sunlight_series(timesteps, base_sunlight, variation):
    # Simulate sunlight variation, e.g., cloud cover impact or day length
    return [
        base_sunlight + random.uniform(-variation, variation) for _ in range(timesteps)
    ]


# Fish-related auxiliaries
fish_auxiliaries = [
    Auxiliary("birth_rate", [0.1] * simulation_time),
    Auxiliary("death_rate_natural", [0.05] * simulation_time),
    Auxiliary("death_rate_fishing", [0.02] * simulation_time),
    Auxiliary("immigration_rate", [0.01] * simulation_time),
]

# Water-related auxiliaries
water_auxiliaries = [
    Auxiliary(
        "water_temperature", generate_temperature_series(simulation_time, 20, 5, 0)
    ),
    Auxiliary("sunlight", [1, 2, 3, 4] * 250),
    Auxiliary("water_pH", [7] * simulation_time),
    Auxiliary("inflow_rate", [0.05] * simulation_time),
    Auxiliary("evaporation_rate", [0.05] * simulation_time),
]

# Nutrient-related auxiliaries
nutrient_auxiliaries = [
    Auxiliary("release_rate", [0.05] * simulation_time),
    Auxiliary("absorption_rate", [0.05] * simulation_time),
]

# Vegetation-related auxiliaries
vegetation_auxiliaries = [
    Auxiliary("vegetation_quantity", [0.05] * simulation_time),
    Auxiliary("vegetation_growth_rate", [0.05] * simulation_time),
    Auxiliary("vegetation_decay_rate", [0.05] * simulation_time),
]

# Combine all auxiliary lists into a single list
auxiliaries = (
    fish_auxiliaries + water_auxiliaries + nutrient_auxiliaries + vegetation_auxiliaries
)


# Initial values for the stocks
# Initial values for the stocks
initial_values = {
    "fish_population": 1000,  # Initial fish population
    # New stocks
    "water_volume": 1000000,  # in litres, for example
    "nutrient_concentration": 50,  # in mg/L, for example
    "aquatic_vegetation": 100,  # in kg, for example
}
# Fish-related rates
fish_rates = {
    "births": {
        "rate_function": lambda fish_population, birth_rate: fish_population
        * birth_rate,
        "source": None,
        "destination": "fish_population",
    },
    "natural_deaths": {
        "rate_function": lambda fish_population, death_rate_natural: fish_population
        * death_rate_natural,
        "source": "fish_population",
        "destination": None,
    },
    "deaths_by_fishing": {
        "rate_function": lambda fish_population, death_rate_fishing: fish_population
        * death_rate_fishing,
        "source": "fish_population",
        "destination": None,
    },
    "immigration": {
        "rate_function": lambda fish_population, immigration_rate: fish_population
        * immigration_rate,
        "source": None,
        "destination": "fish_population",
    },
}

# Water-related rates
water_rates = {
    "water_inflow": {
        "rate_function": lambda water_volume, inflow_rate: inflow_rate,
        "source": None,
        "destination": "water_volume",
    },
    "water_evaporation": {
        "rate_function": lambda water_volume, evaporation_rate: water_volume
        * evaporation_rate,
        "source": "water_volume",
        "destination": None,
    },
}

# Nutrient-related rates
nutrient_rates = {
    "nutrient_release": {
        "rate_function": lambda nutrient_concentration, release_rate: nutrient_concentration
        * release_rate,
        "source": None,
        "destination": "nutrient_concentration",
    },
    "nutrient_absorption": {
        "rate_function": lambda nutrient_concentration, absorption_rate: nutrient_concentration
        * absorption_rate,
        "source": "nutrient_concentration",
        "destination": None,
    },
}

# Vegetation-related rates
vegetation_rates = {
    "vegetation_growth": {
        "rate_function": lambda vegetation_quantity, vegetation_growth_rate, nutrient_concentration, sunlight: vegetation_quantity
        * vegetation_growth_rate
        * nutrient_concentration
        * sunlight,
        "source": None,
        "destination": "vegetation_quantity",
    },
    "vegetation_decay": {
        "rate_function": lambda vegetation_quantity, vegetation_decay_rate: vegetation_quantity
        * vegetation_decay_rate,
        "source": "vegetation_quantity",
        "destination": None,
    },
}

# Combine all rates into a single rates dictionary if needed for the simulation
rates = {**fish_rates, **water_rates, **nutrient_rates, **vegetation_rates}

# Define scenarios
base_scenario = Scenario("Base scenario", initial_values, rates, auxiliaries)
overfishing_scenario = Scenario(
    "Overfishing",
    initial_values,
    {
        **rates,
        "deaths_by_fishing": {
            "rate_function": lambda fish_population, death_rate_fishing: fish_population
            * (death_rate_fishing + 0.05),
            "source": "fish_population",
            "destination": None,
        },
    },
    auxiliaries,
)

# Create and run the scenarios
manager = ScenarioManager()
manager.add_scenario(base_scenario)
manager.add_scenario(overfishing_scenario)
manager.run_all(simulation_time=1000, dt=1)

# Get and print results
base_results = manager.get_results("Base scenario")
overfishing_results = manager.get_results("Overfishing")

# Convert results to DataFrame for better visualization
base_df = pd.DataFrame(base_results)
overfishing_df = pd.DataFrame(overfishing_results)

print("Base Scenario Results:")
print(base_df)
print("\nOverfishing Scenario Results:")
print(base_df[["water_temperature", "sunlight"]])
