from __future__ import annotations

import pytest

from models.core.auxiliary import Auxiliary
from models.core.stock import Stock
from models.scenario.scenario import Scenario


@pytest.fixture
def simple_stock() -> Stock:
    return Stock("population", initial_value=100)


@pytest.fixture
def sir_auxiliaries() -> list[Auxiliary]:
    return [
        Auxiliary("transmission_rate", [0.015] * 200),
        Auxiliary("recovery_rate", [0.01] * 200),
    ]


@pytest.fixture
def sir_initial_values() -> dict[str, float]:
    return {"susceptible": 50, "infected": 10, "recovered": 0}


@pytest.fixture
def sir_rates() -> dict:
    return {
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


@pytest.fixture
def sir_scenario(
    sir_initial_values: dict[str, float],
    sir_rates: dict,
    sir_auxiliaries: list[Auxiliary],
) -> Scenario:
    return Scenario("SIR", sir_initial_values, sir_rates, sir_auxiliaries)
