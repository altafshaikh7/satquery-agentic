from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Trace(BaseModel):
    trace_id: str
    query: str
    route: str | None = None
    steps: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )