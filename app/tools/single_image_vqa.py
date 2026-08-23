from typing import Any

from app.tools.base import BaseTool


class SingleImageVQATool(BaseTool):
    name = "single_image_vqa"
    description = (
        "Answers questions about a single remote sensing image"
    )

    def run(self, parameters: dict[str, Any]) -> dict[str, Any]:
        image_urls = parameters.get("image_urls", [])

        if len(image_urls) < 1:
            raise ValueError(
                "Single image VQA requires at least one image URL"
            )

        return {
            "tool": self.name,
            "status": "input_validated",
            "question": parameters.get("query"),
        }