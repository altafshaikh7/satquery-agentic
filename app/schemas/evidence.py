from pydantic import BaseModel, Field


class Evidence(BaseModel):
    evidence_id: str
    source: str
    claim: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)