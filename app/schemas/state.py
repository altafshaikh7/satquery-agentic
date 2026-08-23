from typing import Any

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    run_id: str
    query: str
    route: str | None = None
    plan: list[dict[str, Any]] = Field(default_factory=list)
    results: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float | None = None
    final_answer: str | None = None
    error: str | None = None