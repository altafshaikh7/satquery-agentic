from pathlib import Path
from typing import Any

from PIL import Image

from app.tools.base import BaseTool


class SingleImageVQATool(BaseTool):
    name = "single_image_vqa"
    description = "Answer basic questions about a single image"

    def run(self, parameters: dict[str, Any]) -> dict[str, Any]:
        image_urls = parameters.get("image_urls", [])
        query = parameters.get("query", "")

        if not image_urls:
            raise ValueError(
                "Single image VQA requires at least one image URL"
            )

        image_path = Path(image_urls[0])

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_urls[0]}"
            )

        image = Image.open(image_path).convert("RGB")

        return {
            "tool": self.name,
            "status": "success",
            "query": query,
            "answer": (
                f"The image is available for analysis and has "
                f"a resolution of {image.width} x {image.height} pixels."
            ),
            "image": image_urls[0],
        }