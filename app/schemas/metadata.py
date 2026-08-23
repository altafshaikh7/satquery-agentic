from datetime import datetime

from pydantic import BaseModel


class GeoMetadata(BaseModel):
    crs: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    acquisition_time: datetime | None = None
    satellite: str | None = None
    sensor: str | None = None
    cloud_cover: float | None = None