from pydantic import BaseModel, Field


class ImageInput(BaseModel):
    image_id: str = Field(..., min_length=1)
    path: str | None = None
    url: str | None = None
    sensor_type: str | None = None
    acquisition_date: str | None = None