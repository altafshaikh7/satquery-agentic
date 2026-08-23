from app.tools.base import BaseTool


class ToolRegistry:
    """
    Central registry for all SatQuery analysis tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool using its unique name.
        """
        if not tool.name:
            raise ValueError("Tool must have a non-empty name.")

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")

        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> BaseTool:
        """
        Get a registered tool by name.
        """
        if tool_name not in self._tools:
            available = ", ".join(self._tools.keys()) or "none"
            raise KeyError(
                f"Tool '{tool_name}' is not registered. "
                f"Available tools: {available}"
            )

        return self._tools[tool_name]

    def list_tools(self) -> list[str]:
        """
        Return all registered tool names.
        """
        return list(self._tools.keys())

    def has(self, tool_name: str) -> bool:
        """
        Check whether a tool is registered.
        """
        return tool_name in self._tools