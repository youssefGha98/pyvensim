from abc import ABC, abstractmethod


class SystemComponent(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = name

    @abstractmethod
    def step(self, dt: float) -> None:
        pass
