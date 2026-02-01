import pytest

from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario


class TestScenario:
    def test_construct_simulation(self, sir_scenario: Scenario) -> None:
        sim = sir_scenario.construct_simulation()
        names = [c.name for c in sim.components]
        assert "susceptible" in names
        assert "infected" in names
        assert "recovered" in names
        assert "infection" in names
        assert "recovery" in names

    def test_run_returns_results(self, sir_scenario: Scenario) -> None:
        results = sir_scenario.run(10, 1)
        assert "time" in results
        assert "susceptible" in results
        assert "infected" in results
        assert "recovered" in results

    def test_sir_conservation(self, sir_scenario: Scenario) -> None:
        """Total population (S + I + R) should be conserved in the SIR model."""
        results = sir_scenario.run(100, 1)
        total_initial = 50 + 10 + 0
        for i in range(len(results["time"])):
            total = (
                results["susceptible"][i]
                + results["infected"][i]
                + results["recovered"][i]
            )
            assert total == pytest.approx(total_initial, abs=1e-6)

    def test_results_stored(self, sir_scenario: Scenario) -> None:
        sir_scenario.run(10, 1)
        assert sir_scenario.results is not None
        assert "time" in sir_scenario.results

    def test_sensitivity_analysis_univariate(self, sir_scenario: Scenario) -> None:
        results = sir_scenario.run_sensitivity_analysis_univariate(
            "stocks",
            "susceptible",
            [40, 60],
            until=10,
            dt=1,
        )
        assert len(results) == 2

    def test_sensitivity_analysis_multivariate(self) -> None:
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
                "rate_function": lambda infected, recovery_rate: infected
                * recovery_rate,
                "source": "infected",
                "destination": "recovered",
            },
        }
        scenario = Scenario("SIR", initial_values, rates, auxiliaries)

        parameters = [
            {"component": "stocks", "name": "susceptible"},
            {"component": "stocks", "name": "infected"},
        ]
        combinations = [
            (40, 5),
            (60, 15),
        ]
        results = scenario.run_sensitivity_analysis_multivariate(
            parameters, combinations, until=10, dt=1
        )
        assert len(results) == 2

    def test_apply_shock_auxiliary(self) -> None:
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
                "rate_function": lambda infected, recovery_rate: infected
                * recovery_rate,
                "source": "infected",
                "destination": "recovered",
            },
        }
        scenario = Scenario("SIR", initial_values, rates, auxiliaries)

        components = {
            "transmission_rate": {
                "component_type": "auxiliary",
                "shock_value": 0.1,
                "start_time": 5,
                "end_time": 10,
            },
        }
        scenario.apply_shock_over_period(components, until=20, dt=1)
        assert scenario.results is not None

    def test_apply_shock_invalid_times(self, sir_scenario: Scenario) -> None:
        components = {
            "transmission_rate": {
                "component_type": "auxiliary",
                "shock_value": 0.1,
                "start_time": 10,
                "end_time": 5,
            },
        }
        with pytest.raises(ValueError, match="end_time must be greater"):
            sir_scenario.apply_shock_over_period(components)
