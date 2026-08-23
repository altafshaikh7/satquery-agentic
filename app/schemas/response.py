from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    query_id: str
    session_id: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    status: str
    evidence_count: int = 0
    trace_id: str