from typing import Any

from pydantic import BaseModel


class QueryResponse(BaseModel):
    query: str
    route: str
    tasks: list[dict[str, Any]]
    results: list[dict[str, Any]]