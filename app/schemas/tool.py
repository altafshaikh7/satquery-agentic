from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: dict = Field(default_factory=dict)
    confidence: float | None = None
    error: str | None = None