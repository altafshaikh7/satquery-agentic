from typing import Any

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    query: str
    route: str | None = None

    tasks: list[dict[str, Any]] = Field(
        default_factory=list
    )

    results: list[dict[str, Any]] = Field(
        default_factory=list
    )

    evidence: list[dict[str, Any]] = Field(
        default_factory=list
    )

    verification: dict[str, Any] = Field(
        default_factory=dict
    )

    answer: str | None = None
    confidence: float = 0.0

    error: str | None = None