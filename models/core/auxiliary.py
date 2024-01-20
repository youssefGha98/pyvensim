from .system_component import SystemComponent


class Auxiliary(SystemComponent):
    def __init__(self, name, values=None):
        super().__init__(name)
        self.values = values
        self.current_time_step = 0

    def value(self):
        if callable(self.values):
            return self.values()

        elif isinstance(self.values, list):
            if self.current_time_step < len(self.values):
                return self.values[self.current_time_step]
            else:
                return self.values[-1]

        else:
            return self.values

    def step(self, dt):
        self.current_time_step += 1
