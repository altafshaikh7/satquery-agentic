from typing import Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's remote sensing query")
    image_urls: list[str] = Field(
        default_factory=list,
        description="Optional satellite or remote sensing image URLs",
    )
    session_id: Optional[str] = None