from typing import Any

from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    query: str
    route: str
    tasks: list[dict[str, Any]] = Field(default_factory=list)
    results: list[dict[str, Any]] = Field(default_factory=list)
    answer: str | None = None
    confidence: float = 0.0
    trace_id: str | None = None