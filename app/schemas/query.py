from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language remote sensing query",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional session identifier",
    )