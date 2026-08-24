from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    """
    Request schema for SatQuery AI.

    The user must provide a natural-language query.

    image_urls and bbox are optional:
    - image_urls can contain user-provided image paths or URLs.
    - bbox can define the target geographic area.
    - before_date and after_date are used for temporal
      change analysis.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="Remote sensing question or analysis request",
    )

    image_urls: list[str] = Field(
        default_factory=list,
        description="Optional local image paths or image URLs",
    )

    bbox: Optional[list[float]] = Field(
        default=None,
        description=(
            "Optional bounding box in the format: "
            "[min_lon, min_lat, max_lon, max_lat]."
        ),
    )

    before_date: Optional[date] = Field(
        default=None,
        description=(
            "Optional start date for change analysis "
            "in YYYY-MM-DD format."
        ),
    )

    after_date: Optional[date] = Field(
        default=None,
        description=(
            "Optional end date for change analysis "
            "in YYYY-MM-DD format."
        ),
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("query cannot be empty.")

        return cleaned_value

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(
        cls,
        image_urls: list[str],
    ) -> list[str]:
        return [
            image_url.strip()
            for image_url in image_urls
            if image_url and image_url.strip()
        ]

    @field_validator("bbox")
    @classmethod
    def validate_bbox(
        cls,
        bbox: Optional[list[float]],
    ) -> Optional[list[float]]:
        if bbox is None:
            return None

        if len(bbox) != 4:
            raise ValueError(
                "bbox must contain exactly 4 values: "
                "[min_lon, min_lat, max_lon, max_lat]."
            )

        min_lon, min_lat, max_lon, max_lat = bbox

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
                "bbox min_lon must be between -180 and 180."
            )

        if not (-180 <= max_lon <= 180):
            raise ValueError(
                "bbox max_lon must be between -180 and 180."
            )

        if not (-90 <= min_lat <= 90):
            raise ValueError(
                "bbox min_lat must be between -90 and 90."
            )

        if not (-90 <= max_lat <= 90):
            raise ValueError(
                "bbox max_lat must be between -90 and 90."
            )

        return [
            float(min_lon),
            float(min_lat),
            float(max_lon),
            float(max_lat),
        ]

    @field_validator("after_date")
    @classmethod
    def validate_after_date(
        cls,
        after_date: Optional[date],
        info,
    ) -> Optional[date]:
        if after_date is None:
            return after_date

        before_date = info.data.get("before_date")

        if (
            before_date is not None
            and after_date <= before_date
        ):
            raise ValueError(
                "after_date must be later than before_date."
            )

        return after_date