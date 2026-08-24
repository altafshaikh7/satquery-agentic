from typing import Any

from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    source: str | None = None
    timestamp: str | None = None
    satellite: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)