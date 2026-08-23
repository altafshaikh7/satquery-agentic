from typing import Any

from app.tools.base import BaseTool


class ChangeAnalysisTool(BaseTool):
    name = "change_analysis"
    description = (
        "Analyzes differences between two or more remote sensing images"
    )

    def run(self, parameters: dict[str, Any]) -> dict[str, Any]:
        image_urls = parameters.get("image_urls", [])

        if len(image_urls) < 2:
            raise ValueError(
                "Change analysis requires at least two image URLs"
            )

        return {
            "tool": self.name,
            "status": "ready",
            "image_count": len(image_urls),
            "message": (
                "Change analysis input validated successfully. "
                "Real satellite image processing will be executed "
                "in the image analysis pipeline."
            ),
        }