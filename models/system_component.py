class SystemComponent:
    def __init__(self, name):
        self.name = name

    def step(self, dt):
        pass  # Sera redéfini dans les sous-classes
