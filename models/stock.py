from .system_component import SystemComponent
import numpy as np


class Stock(SystemComponent):
    def __init__(self, name, initial_value=0):
        super().__init__(name)
        self.value = initial_value

    def change(self, amount):
        new_value = self.value + amount
        if not np.isfinite(
            new_value
        ):  # Vérifier si la nouvelle valeur est infinie ou NaN
            raise ValueError("Stock value became non-finite")
        self.value = new_value

    def step(self, dt):
        # La méthode step pour Stock pourrait inclure une logique pour le changement de valeur au fil du temps
        pass
