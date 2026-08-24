from typing import Any

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    tool_name: str
    status: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None