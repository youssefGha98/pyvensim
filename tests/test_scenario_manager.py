from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario
from models.scenario.scenario_manager import ScenarioManager


def _make_scenario(name: str) -> Scenario:
    auxiliaries = [
        Auxiliary("transmission_rate", [0.015] * 200),
        Auxiliary("recovery_rate", [0.01] * 200),
    ]
    initial_values = {"susceptible": 50, "infected": 10, "recovered": 0}
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
    return Scenario(name, initial_values, rates, auxiliaries)


class TestScenarioManager:
    def test_add_scenario(self) -> None:
        mgr = ScenarioManager()
        s = _make_scenario("test")
        mgr.add_scenario(s)
        assert len(mgr.scenarios) == 1

    def test_run_all(self) -> None:
        mgr = ScenarioManager()
        mgr.add_scenario(_make_scenario("s1"))
        mgr.add_scenario(_make_scenario("s2"))
        mgr.run_all(simulation_time=10, dt=1)
        assert mgr.scenarios[0].results is not None
        assert mgr.scenarios[1].results is not None

    def test_get_results(self) -> None:
        mgr = ScenarioManager()
        mgr.add_scenario(_make_scenario("s1"))
        mgr.run_all(simulation_time=10, dt=1)
        results = mgr.get_results("s1")
        assert results is not None
        assert "time" in results

    def test_get_results_unknown(self) -> None:
        mgr = ScenarioManager()
        assert mgr.get_results("unknown") is None
