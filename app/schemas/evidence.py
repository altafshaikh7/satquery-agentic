from pydantic import BaseModel


class Evidence(BaseModel):
    evidence_id: str
    source: str
    description: str
    confidence: float = 0.0