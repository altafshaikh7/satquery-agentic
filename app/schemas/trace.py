from datetime import datetime

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    trace_id: str
    event_type: str
    timestamp: datetime
    message: str
    data: dict = Field(default_factory=dict)