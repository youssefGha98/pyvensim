from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.session import store


@pytest.fixture
def client() -> TestClient:
    """Fresh TestClient with cleared session store."""
    store._sessions.clear()
    return TestClient(app)


@pytest.fixture
def sir_payload() -> dict[str, Any]:
    """A complete SIR model as a JSON-ready dict."""
    return {
        "name": "SIR Model",
        "initial_values": {
            "susceptible": 50,
            "infected": 10,
            "recovered": 0,
        },
        "rates": {
            "infection": {
                "expression": "susceptible * infected * transmission_rate",
                "params": [
                    "susceptible",
                    "infected",
                    "transmission_rate",
                ],
                "source": "susceptible",
                "destination": "infected",
            },
            "recovery": {
                "expression": "infected * recovery_rate",
                "params": ["infected", "recovery_rate"],
                "source": "infected",
                "destination": "recovered",
            },
        },
        "auxiliaries": [
            {"name": "transmission_rate", "values": [0.015] * 200},
            {"name": "recovery_rate", "values": [0.01] * 200},
        ],
    }
