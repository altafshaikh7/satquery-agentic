from typing import Any

from pydantic import BaseModel, Field


class ImageInput(BaseModel):
    image_id: str | None = None
    uri: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language remote sensing query",
    )
    session_id: str | None = None
    images: list[ImageInput] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)