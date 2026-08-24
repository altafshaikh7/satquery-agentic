from app.memory.base import BaseMemory


class ExecutionMemory(BaseMemory):
    def __init__(self):
        self._data: dict[str, dict] = {}

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value):
        self._data[key] = value