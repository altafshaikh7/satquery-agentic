from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base class for SatQuery tools"

    @abstractmethod
    def run(self, parameters: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError