from pydantic import BaseModel


class ImageInput(BaseModel):
    url: str
    image_type: str | None = None