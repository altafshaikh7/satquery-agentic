from pathlib import Path
from typing import Any

from PIL import Image

from app.tools.base import BaseTool


class SceneCaptionTool(BaseTool):
    name = "scene_caption"
    description = "Generate a basic description for a satellite image"

    def run(self, parameters: dict[str, Any]) -> dict[str, Any]:
        image_urls = parameters.get("image_urls", [])

        if not image_urls:
            raise ValueError(
                "Scene captioning requires at least one image URL"
            )

        image_path = Path(image_urls[0])

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_urls[0]}"
            )

        image = Image.open(image_path).convert("RGB")

        width, height = image.size

        return {
            "tool": self.name,
            "status": "success",
            "caption": (
                "Satellite or aerial image received for analysis. "
                f"The image resolution is {width} x {height} pixels."
            ),
            "image": image_urls[0],
            "width": width,
            "height": height,
        }