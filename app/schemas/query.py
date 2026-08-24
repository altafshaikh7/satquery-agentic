from typing import Optional

from pydantic import BaseModel, Field, model_validator


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Remote sensing question or analysis request",
    )

    image_urls: list[str] = Field(
        default_factory=list,
        description="Optional local image paths",
    )

    bbox: Optional[list[float]] = Field(
        default=None,
        description=(
            "Optional bounding box in the format: "
            "[min_lon, min_lat, max_lon, max_lat]"
        ),
    )

    @model_validator(mode="after")
    def validate_image_or_bbox(self):
        if not self.image_urls and self.bbox is None:
            raise ValueError(
                "Provide either 'image_urls' or 'bbox'."
            )

        if self.bbox is not None:
            if len(self.bbox) != 4:
                raise ValueError(
                    "bbox must contain exactly 4 values: "
                    "[min_lon, min_lat, max_lon, max_lat]"
                )

            min_lon, min_lat, max_lon, max_lat = self.bbox

            if min_lon >= max_lon:
                raise ValueError(
                    "bbox min_lon must be smaller than max_lon."
                )

            if min_lat >= max_lat:
                raise ValueError(
                    "bbox min_lat must be smaller than max_lat."
                )

            if not (-180 <= min_lon <= 180):
                raise ValueError(
                    "bbox longitude values must be between -180 and 180."
                )

            if not (-180 <= max_lon <= 180):
                raise ValueError(
                    "bbox longitude values must be between -180 and 180."
                )

            if not (-90 <= min_lat <= 90):
                raise ValueError(
                    "bbox latitude values must be between -90 and 90."
                )

            if not (-90 <= max_lat <= 90):
                raise ValueError(
                    "bbox latitude values must be between -90 and 90."
                )

        return self