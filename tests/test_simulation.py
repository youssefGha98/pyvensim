import pytest

from models.core.auxiliary import Auxiliary
from models.core.flow import Flow
from models.core.stock import Stock
from models.engine.simulation import Simulation


def _build_simple_sim() -> Simulation:
    """Build a simple simulation: stock grows by constant rate."""
    stock = Stock("pop", 100)
    aux = Auxiliary("rate", lambda: 10)
    flow = Flow("growth", destination=stock, rate_function=lambda: aux.value())

    sim = Simulation()
    sim.add_component(stock)
    sim.add_component(flow)
    sim.add_component(aux)
    return sim


class TestSimulation:
    def test_run_returns_history(self) -> None:
        sim = _build_simple_sim()
        history = sim.run(until=5, dt=1)
        assert "time" in history
        assert "pop" in history

    def test_run_correct_time_steps(self) -> None:
        sim = _build_simple_sim()
        history = sim.run(until=5, dt=1)
        assert history["time"] == [0, 1, 2, 3, 4]

    def test_stock_grows(self) -> None:
        sim = _build_simple_sim()
        history = sim.run(until=3, dt=1)
        # Each step adds 10 to destination
        assert history["pop"][0] == pytest.approx(110)
        assert history["pop"][1] == pytest.approx(120)
        assert history["pop"][2] == pytest.approx(130)

    def test_continue_run_extends_history(self) -> None:
        sim = _build_simple_sim()
        sim.run(until=3, dt=1)
        sim.continue_run({"pop": 200}, until=5, dt=1)
        assert len(sim.history["time"]) > 3

    def test_get_results_returns_history(self) -> None:
        sim = _build_simple_sim()
        sim.run(until=3, dt=1)
        assert sim.get_results() is sim.history

    def test_empty_simulation_runs(self) -> None:
        sim = Simulation()
        history = sim.run(until=3, dt=1)
        assert history["time"] == [0, 1, 2]
