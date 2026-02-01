import pytest

from models.calibration.calibrator import Calibrator
from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario


def _make_scenario() -> Scenario:
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
    return Scenario("SIR", initial_values, rates, auxiliaries)


class TestCalibrator:
    def test_init_default_params(self) -> None:
        s = _make_scenario()
        cal = Calibrator(s)
        assert cal.simulation_time == 91
        assert cal.dt == 1

    def test_init_custom_params(self) -> None:
        s = _make_scenario()
        cal = Calibrator(s, simulation_time=50, dt=0.5)
        assert cal.simulation_time == 50
        assert cal.dt == 0.5

    def test_unsupported_method(self) -> None:
        s = _make_scenario()
        cal = Calibrator(s)
        with pytest.raises(ValueError, match="not supported"):
            cal.calibrate(None, method="gradient_descent")  # type: ignore[arg-type]

    def test_get_initial_params_list_values(self) -> None:
        s = _make_scenario()
        cal = Calibrator(s)
        params = cal._get_initial_params()
        assert params == [0.015, 0.01]

    def test_get_initial_params_scalar_values(self) -> None:
        auxiliaries = [
            Auxiliary("a", 1.0),
            Auxiliary("b", 2.0),
        ]
        initial_values = {"x": 0}
        rates = {
            "flow": {
                "rate_function": lambda x, a: x * a,
                "source": None,
                "destination": "x",
            }
        }
        s = Scenario("test", initial_values, rates, auxiliaries)
        cal = Calibrator(s)
        params = cal._get_initial_params()
        assert params == [1.0, 2.0]
