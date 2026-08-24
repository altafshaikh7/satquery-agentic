from abc import ABC, abstractmethod


class BaseMemory(ABC):
    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value):
        pass