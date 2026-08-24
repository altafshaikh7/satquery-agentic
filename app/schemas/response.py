from typing import Any

from pydantic import BaseModel


class QueryResponse(BaseModel):
    query: str
    route: str

    tasks: list[dict[str, Any]]
    results: list[dict[str, Any]]

    evidence: list[dict[str, Any]]
    verification: dict[str, Any]

    answer: str
    confidence: float