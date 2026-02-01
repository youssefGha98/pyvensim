import pytest

from models.core.flow import Flow
from models.core.stock import Stock


class TestFlow:
    def test_source_decreases(self) -> None:
        src = Stock("src", 100)
        flow = Flow("f", source=src, rate_function=lambda: 10)
        flow.step(1)
        assert src.value == 90

    def test_destination_increases(self) -> None:
        dst = Stock("dst", 0)
        flow = Flow("f", destination=dst, rate_function=lambda: 10)
        flow.step(1)
        assert dst.value == 10

    def test_source_and_destination_transfer(self) -> None:
        src = Stock("src", 100)
        dst = Stock("dst", 0)
        flow = Flow("f", source=src, destination=dst, rate_function=lambda: 5)
        flow.step(1)
        assert src.value == 95
        assert dst.value == 5

    def test_dt_scaling(self) -> None:
        src = Stock("src", 100)
        flow = Flow("f", source=src, rate_function=lambda: 10)
        flow.step(0.5)
        assert src.value == pytest.approx(95)

    def test_no_rate_function_does_nothing(self) -> None:
        src = Stock("src", 100)
        flow = Flow("f", source=src)
        flow.step(1)
        assert src.value == 100

    def test_noise_changes_value(self) -> None:
        src = Stock("src", 1000)
        flow = Flow("f", source=src, rate_function=lambda: 10, add_noise=True, sensitivity=0.5)

        values = set()
        for _ in range(20):
            src.value = 1000
            flow.step(1)
            values.add(round(src.value, 6))

        # With noise and sensitivity=0.5, we should get some variation
        assert len(values) > 1
