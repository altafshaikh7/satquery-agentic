from typing import Any

from app.tools.base import BaseTool


class SceneCaptionTool(BaseTool):
    name = "scene_caption"
    description = "Generates a description for a remote sensing image"

    def run(self, parameters: dict[str, Any]) -> dict[str, Any]:
        image_urls = parameters.get("image_urls", [])

        if len(image_urls) < 1:
            raise ValueError(
                "Scene captioning requires at least one image URL"
            )

        return {
            "tool": self.name,
            "status": "input_validated",
            "image_count": len(image_urls),
        }