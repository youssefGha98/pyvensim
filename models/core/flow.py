from __future__ import annotations

import random
from collections.abc import Callable
from typing import TYPE_CHECKING

from .system_component import SystemComponent

if TYPE_CHECKING:
    from .stock import Stock


class Flow(SystemComponent):
    def __init__(
        self,
        name: str,
        source: Stock | None = None,
        destination: Stock | None = None,
        rate_function: Callable[[], float] | None = None,
        add_noise: bool = False,
        sensitivity: float = 0.1,
    ) -> None:
        super().__init__(name)
        self.source = source
        self.destination = destination
        self.rate_function = rate_function
        self.add_noise = add_noise
        self.sensitivity = sensitivity

    def step(self, dt: float) -> None:
        if callable(self.rate_function):
            flow_rate = self.rate_function()

            if self.add_noise:
                flow_rate += flow_rate * random.uniform(
                    -self.sensitivity, self.sensitivity
                )

            if self.source:
                self.source.change(-flow_rate * dt)
            if self.destination:
                self.destination.change(flow_rate * dt)
