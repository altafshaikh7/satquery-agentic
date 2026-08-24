from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    image_urls: list[str] = Field(default_factory=list)
    session_id: str | None = None