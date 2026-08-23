from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Base interface for every SatQuery remote-sensing analysis tool.
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        Execute the tool and return a structured result.
        """
        raise NotImplementedError

    def validate_input(self, **kwargs: Any) -> None:
        """
        Override in specialized tools when input validation is required.
        """
        return None