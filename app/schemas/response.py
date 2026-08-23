from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence


class QueryResponse(BaseModel):
    run_id: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)
    trace_id: str | None = None