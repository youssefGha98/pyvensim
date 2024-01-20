from .system_component import SystemComponent


class Auxiliary(SystemComponent):
    def __init__(self, name, values=None):
        super().__init__(name)
        # values can be a list or a callable
        self.values = values
        self.current_time_step = 0

    def value(self):
        # If values is a callable, it behaves as before
        if callable(self.values):
            return self.values()

        # If values is a list, it returns the value at the current timestep
        elif isinstance(self.values, list):
            # If the list is shorter than the current time step, repeat the last value
            if self.current_time_step < len(self.values):
                return self.values[self.current_time_step]
            else:
                return self.values[-1]

        # If values is neither a callable nor a list, it's a constant value
        else:
            return self.values

    def step(self, dt):
        # Increment the timestep
        self.current_time_step += 1
