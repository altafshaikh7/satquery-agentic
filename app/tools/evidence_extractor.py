from typing import Any


class EvidenceExtractor:

    def extract(
        self,
        result: dict[str, Any],
    ) -> list[dict[str, Any]]:

        evidence = []

        if result.get("status") != "success":
            return evidence

        tool = result.get("tool", "unknown")

        # --------------------------------------------------
        # GENERAL TOOL EVIDENCE
        # --------------------------------------------------

        evidence.append(
            {
                "source": tool,
                "description": "Tool execution completed successfully.",
                "confidence": 0.70,
            }
        )

        # --------------------------------------------------
        # SENTINEL METADATA
        # --------------------------------------------------

        sentinel = result.get("sentinel")

        if sentinel:
            evidence.append(
                {
                    "source": "sentinel_metadata",
                    "description": (
                        "Satellite imagery metadata is available."
                    ),
                    "product_id": sentinel.get("product_id"),
                    "datetime": sentinel.get("datetime"),
                    "cloud_cover": sentinel.get("cloud_cover"),
                    "confidence": 0.90,
                }
            )

        # --------------------------------------------------
        # CHANGE ANALYSIS EVIDENCE
        # --------------------------------------------------

        if tool == "change_analysis":

            if result.get("change_detected") is not None:
                evidence.append(
                    {
                        "source": "change_detection",
                        "description": (
                            "Pixel-level change analysis completed."
                        ),
                        "change_percentage": result.get(
                            "change_percentage"
                        ),
                        "changed_pixels": result.get(
                            "changed_pixels"
                        ),
                        "total_pixels": result.get(
                            "total_pixels"
                        ),
                        "confidence": 0.90,
                    }
                )

            if result.get("vegetation_status"):
                evidence.append(
                    {
                        "source": "ndvi_analysis",
                        "description": (
                            "Vegetation change was evaluated "
                            "using NDVI."
                        ),
                        "vegetation_status": result.get(
                            "vegetation_status"
                        ),
                        "mean_ndvi_before": result.get(
                            "mean_ndvi_before"
                        ),
                        "mean_ndvi_after": result.get(
                            "mean_ndvi_after"
                        ),
                        "ndvi_change": result.get(
                            "ndvi_change"
                        ),
                        "confidence": 0.95,
                    }
                )

        # --------------------------------------------------
        # IMAGE ANALYSIS EVIDENCE
        # --------------------------------------------------

        if tool in {
            "scene_caption",
            "single_image_vqa",
        }:
            evidence.append(
                {
                    "source": "vision_analysis",
                    "description": (
                        "Analysis was generated from the "
                        "provided satellite or aerial image."
                    ),
                    "image": result.get("image"),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "model": result.get("model"),
                    "confidence": 0.80,
                }
            )

        return evidence