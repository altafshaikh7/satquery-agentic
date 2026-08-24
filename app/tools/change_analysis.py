from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops

from app.tools.base import BaseTool


class ChangeAnalysisTool(BaseTool):
    name = "change_analysis"
    description = "Detect changes between two satellite images"

    def run(self, parameters: dict[str, Any]) -> dict[str, Any]:
        image_urls = parameters.get("image_urls", [])
        threshold = parameters.get("change_threshold", 30)

        if len(image_urls) < 2:
            raise ValueError(
                "Change analysis requires at least two image URLs"
            )

        before_image = self._load_image(image_urls[0])
        after_image = self._load_image(image_urls[1])

        before_image, after_image = self._resize_to_match(
            before_image,
            after_image,
        )

        difference = ImageChops.difference(before_image, after_image)
        difference_array = np.array(difference)

        if difference_array.ndim == 3:
            change_mask = np.max(difference_array, axis=2) > threshold
        else:
            change_mask = difference_array > threshold

        changed_pixels = int(np.sum(change_mask))
        total_pixels = int(change_mask.size)

        change_percentage = round(
            (changed_pixels / total_pixels) * 100,
            2,
        )

        return {
            "tool": self.name,
            "status": "success",
            "before_image": image_urls[0],
            "after_image": image_urls[1],
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "change_percentage": change_percentage,
            "change_detected": change_percentage > 0,
        }

    def _load_image(self, image_path: str) -> Image.Image:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        return Image.open(path).convert("RGB")

    def _resize_to_match(
        self,
        first: Image.Image,
        second: Image.Image,
    ) -> tuple[Image.Image, Image.Image]:
        if first.size == second.size:
            return first, second

        second = second.resize(first.size)
        return first, second