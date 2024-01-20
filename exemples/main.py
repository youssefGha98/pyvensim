from models.stock import Stock
from models.flow import Flow
from models.simulation import Simulation
from models.auxiliary import Auxiliary
from models.equation import Equation
from models.scenario import Scenario
from models.scenario_manager import ScenarioManager

# Stocks
rabbits = Stock("rabbits", 100)
foxes = Stock("foxes", 20)

# Variables auxiliaires
rabbit_reproduction_rate = Auxiliary("rabbit_reproduction_rate", lambda: 0.1)
hunting_rate = Auxiliary("hunting_rate", lambda: 0.02)
fox_reproduction_rate = Auxiliary("fox_reproduction_rate", lambda: 0.01)
fox_death_rate = Auxiliary("fox_death_rate", lambda: 0.1)

# Paramètres de bruit
add_noise = False
sensitivity = 0

# Equations
# Définition des équations
rabbit_birth_equation = Equation(
    lambda rabbits, rabbit_reproduction_rate: rabbits * rabbit_reproduction_rate
)
rabbit_death_equation = Equation(
    lambda rabbits, foxes, hunting_rate: rabbits * foxes * hunting_rate
)
fox_birth_equation = Equation(
    lambda rabbits, foxes, fox_reproduction_rate: rabbits
    * foxes
    * fox_reproduction_rate
)
fox_death_equation = Equation(lambda foxes, fox_death_rate: foxes * fox_death_rate)

# Utilisation des équations dans les flux
rabbit_birth = Flow(
    "rabbit_birth",
    source=None,
    destination=rabbits,
    rate_function=lambda: rabbit_birth_equation.evaluate(
        rabbits=rabbits.value, rabbit_reproduction_rate=rabbit_reproduction_rate.value()
    ),
)

rabbit_death = Flow(
    "rabbit_death",
    source=rabbits,
    destination=None,
    rate_function=lambda: rabbit_death_equation.evaluate(
        rabbits=rabbits.value, foxes=foxes.value, hunting_rate=hunting_rate.value()
    ),
)

fox_birth = Flow(
    "fox_birth",
    source=None,
    destination=foxes,
    rate_function=lambda: fox_birth_equation.evaluate(
        rabbits=rabbits.value,
        foxes=foxes.value,
        fox_reproduction_rate=fox_reproduction_rate.value(),
    ),
)

fox_death = Flow(
    "fox_death",
    source=foxes,
    destination=None,
    rate_function=lambda: fox_death_equation.evaluate(
        foxes=foxes.value, fox_death_rate=fox_death_rate.value()
    ),
)


# Création de la simulation
simulation = Simulation()
simulation.add_component(rabbits)
simulation.add_component(foxes)
simulation.add_component(rabbit_birth)
simulation.add_component(rabbit_death)
simulation.add_component(fox_birth)
simulation.add_component(fox_death)

# Exécution de la simulation
result = simulation.run(until=100, dt=1)
print(result)

# # Define some scenarios
# scenario1 = Scenario("Base Scenario", {'rabbits': 100, 'foxes': 20}, {'rabbit_reproduction_rate': 0.1, 'hunting_rate': 0.02, ...})
# scenario2 = Scenario("High Rabbits", {'rabbits': 200, 'foxes': 20}, {'rabbit_reproduction_rate': 0.1, 'hunting_rate': 0.02, ...})

# # Add scenarios to the manager
# manager = ScenarioManager()
# manager.add_scenario(scenario1)
# manager.add_scenario(scenario2)

# # Run all scenarios
# manager.run_all()

# # Get results for a specific scenario
# results = manager.get_results("Base Scenario")
