from .system_component import SystemComponent
import random


class Flow(SystemComponent):
    def __init__(
        self,
        name,
        source=None,
        destination=None,
        rate_function=None,
        add_noise=False,
        sensitivity=0.1,
    ):
        super().__init__(name)
        self.source = source
        self.destination = destination
        self.rate_function = rate_function
        self.add_noise = add_noise
        self.sensitivity = sensitivity

    def step(self, dt):
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
