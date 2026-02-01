from .system_component import SystemComponent
import numpy as np


class Stock(SystemComponent):
    def __init__(self, name: str, initial_value: float = 0) -> None:
        super().__init__(name)
        self.value: float = initial_value

    def change(self, amount: float) -> None:
        new_value = self.value + amount
        if not np.isfinite(
            new_value
        ):  # Check if the new value is infinite or NaN
            raise ValueError("Stock value became non-finite")
        self.value = new_value

    def step(self, dt: float) -> None:
        # The step method for Stock could include logic for value changes over time
        pass
