from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from app.tools.base import BaseTool


class ChangeAnalysisTool(BaseTool):
    """
    Performs pixel-level change analysis between two images.
    """

    name = "change_analysis"
    description = "Detects visual changes between two satellite images."

    def _load_image(self, image_path: str) -> np.ndarray:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = Image.open(path).convert("RGB")
        return np.asarray(image, dtype=np.float32)

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        before_path = kwargs.get("before_image")
        after_path = kwargs.get("after_image")
        threshold = float(kwargs.get("threshold", 25.0))

        if not before_path or not after_path:
            raise ValueError(
                "change_analysis requires 'before_image' and 'after_image'."
            )

        before = self._load_image(before_path)
        after = self._load_image(after_path)

        if before.shape != after.shape:
            raise ValueError(
                f"Images must have the same dimensions. "
                f"Got {before.shape} and {after.shape}."
            )

        difference = np.abs(after - before)
        grayscale_difference = np.mean(difference, axis=2)

        changed_mask = grayscale_difference >= threshold
        changed_pixels = int(np.sum(changed_mask))
        total_pixels = int(changed_mask.size)

        change_percentage = (
            (changed_pixels / total_pixels) * 100
            if total_pixels > 0
            else 0.0
        )

        mean_difference = float(np.mean(grayscale_difference))

        return {
            "tool": self.name,
            "before_image": str(before_path),
            "after_image": str(after_path),
            "image_shape": list(before.shape),
            "threshold": threshold,
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "change_percentage": round(change_percentage, 4),
            "mean_pixel_difference": round(mean_difference, 4),
        }