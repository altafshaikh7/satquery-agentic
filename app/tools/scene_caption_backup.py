import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

from app.data_sources.sentinel_provider import SentinelProvider
from app.tools.base import BaseTool


load_dotenv()


class SceneCaptionTool(BaseTool):
    """
    Analyze Sentinel-2 satellite imagery using Gemini Vision.

    When a change_analysis dependency is available, this tool
    analyzes the before and after images and produces a temporal
    comparison instead of downloading an unrelated latest image.
    """

    name = "scene_caption"

    description = (
        "Analyze Sentinel-2 satellite imagery and, when available, "
        "compare before and after observations using Gemini Vision."
    )

    def __init__(self) -> None:
        self.gemini_api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not self.gemini_api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY is missing. "
                "Add one to your .env file."
            )

        self.gemini_model = (
            os.getenv("GEMINI_MODEL")
            or "gemini-3.6-flash"
        )

        self.client = genai.Client(
            api_key=self.gemini_api_key
        )

        self.sentinel_provider = SentinelProvider()

    # =========================================================
    # GET IMAGE
    # =========================================================

    def _get_image_path(
        self,
        parameters: dict[str, Any],
    ) -> tuple[str, dict[str, Any] | None]:

        image_urls = parameters.get(
            "image_urls",
            [],
        )

        if image_urls:

            if not isinstance(
                image_urls,
                list,
            ):
                raise ValueError(
                    "'image_urls' must be a list."
                )

            image_path = Path(
                image_urls[0]
            )

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Image file not found: "
                    f"{image_urls[0]}"
                )

            return str(image_path), None

        bbox = parameters.get("bbox")

        if bbox:

            if (
                not isinstance(bbox, list)
                or len(bbox) != 4
            ):
                raise ValueError(
                    "bbox must contain exactly 4 values: "
                    "[min_lon, min_lat, max_lon, max_lat]"
                )

            result = (
                self.sentinel_provider
                .download_best_sentinel2_image(
                    bbox=bbox,
                    output_path=(
                        "data/latest_scene_sentinel2.png"
                    ),
                    lookback_days=180,
                    max_cloud_coverage=80.0,
                )
            )

            return result["image_path"], result

        raise ValueError(
            "Provide either 'image_urls' or 'bbox'."
        )

    # =========================================================
    # EXTRACT CHANGE ANALYSIS DEPENDENCY
    # =========================================================

    def _get_change_analysis(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any] | None:

        dependency_results = parameters.get(
            "dependency_results",
            {},
        )

        if not isinstance(
            dependency_results,
            dict,
        ):
            return None

        for dependency in (
            dependency_results.values()
        ):

            if not isinstance(
                dependency,
                dict,
            ):
                continue

            if (
                dependency.get("task_type")
                == "change_analysis"
            ):

                result = dependency.get(
                    "result"
                )

                if isinstance(
                    result,
                    dict,
                ):
                    return result

        return None

    # =========================================================
    # ANALYZE SINGLE IMAGE WITH GEMINI
    # =========================================================

    def _analyze_image(
        self,
        image_path: str,
        user_question: str | None = None,
        temporal_label: str | None = None,
    ) -> str:

        image = Image.open(
            image_path
        ).convert("RGB")

        prompt = """
You are an expert Earth Observation and remote sensing analyst.

Analyze this real Sentinel-2 satellite image carefully.

Describe only what is visually observable.

Consider:

- Vegetation and forest cover
- Agricultural land and crop patterns
- Urban or built-up areas
- Roads or visible linear infrastructure
- Rivers, lakes, reservoirs, or other water bodies
- Terrain and land-use patterns
- Spatial distribution of major land-cover classes

Important rules:

- Do not invent precise place names.
- Do not invent events or facts not supported by the image.
- Clearly distinguish observation from uncertainty.
- Do not claim exact measurements unless supported by data.
- Do not claim temporal change from this single image alone.
- Keep the analysis focused on observable Earth Observation evidence.
"""

        if temporal_label:

            prompt += (
                "\n\nThis image represents the "
                f"{temporal_label} observation."
            )

        if user_question:

            prompt += (
                "\n\nThe user specifically asks:\n"
                f"{user_question}"
            )

        try:

            response = (
                self.client.models.generate_content(
                    model=self.gemini_model,
                    contents=[
                        prompt,
                        image,
                    ],
                    config=(
                        types.GenerateContentConfig(
                            temperature=0.2,
                        )
                    ),
                )
            )

        except Exception as error:

            raise RuntimeError(
                "Gemini image analysis failed: "
                f"{error}"
            ) from error

        if not response.text:

            raise RuntimeError(
                "Gemini did not return an image analysis."
            )

        return response.text.strip()

    # =========================================================
    # COMPARE BEFORE + AFTER IMAGES
    # =========================================================

    def _compare_images(
        self,
        before_path: str,
        after_path: str,
        user_question: str | None,
        change_data: dict[str, Any],
    ) -> str:

        before_image = Image.open(
            before_path
        ).convert("RGB")

        after_image = Image.open(
            after_path
        ).convert("RGB")

        change_percentage = (
            change_data.get(
                "change_percentage"
            )
        )

        mean_ndvi_before = (
            change_data.get(
                "mean_ndvi_before"
            )
        )

        mean_ndvi_after = (
            change_data.get(
                "mean_ndvi_after"
            )
        )

        ndvi_change = (
            change_data.get(
                "ndvi_change"
            )
        )

        vegetation_status = (
            change_data.get(
                "vegetation_status"
            )
        )

        before_date = (
            change_data.get(
                "before_sentinel",
                {},
            ).get("datetime")
        )

        after_date = (
            change_data.get(
                "after_sentinel",
                {},
            ).get("datetime")
        )

        prompt = f"""
You are an expert Earth Observation and remote sensing analyst.

You are given TWO Sentinel-2 satellite images of the SAME
geographic region.

Image 1 is the BEFORE observation.
Image 2 is the AFTER observation.

Your task is to perform a visual temporal comparison while using
the provided quantitative change-analysis evidence.

Quantitative evidence:

- Overall pixel-level change: {change_percentage}%
- Mean NDVI before: {mean_ndvi_before}
- Mean NDVI after: {mean_ndvi_after}
- NDVI change: {ndvi_change}
- Overall vegetation status: {vegetation_status}
- Before observation date: {before_date}
- After observation date: {after_date}

Analyze the temporal changes in:

1. Overall land cover
2. Vegetation and forest cover
3. Agricultural areas and crop patterns
4. Water bodies, reservoirs, rivers, and drainage
5. Built-up areas and visible infrastructure
6. Major spatial patterns and environmental changes

Important rules:

- Compare only visually observable differences between the two images.
- Use the numerical evidence as supporting evidence.
- Do not say that only one image is available.
- Do not invent precise locations, events, causes, or land-use
  changes that cannot be verified.
- Do not confuse seasonal variation with permanent land-cover
  change unless the evidence strongly supports it.
- Clearly mention uncertainty where appropriate.
- Distinguish quantitative results from visual interpretation.
- Produce a concise but comprehensive comparison.
"""

        if user_question:

            prompt += (
                "\n\nThe user specifically asks:\n"
                f"{user_question}"
            )

        try:

            response = (
                self.client.models.generate_content(
                    model=self.gemini_model,
                    contents=[
                        prompt,
                        before_image,
                        after_image,
                    ],
                    config=(
                        types.GenerateContentConfig(
                            temperature=0.2,
                        )
                    ),
                )
            )

        except Exception as error:

            raise RuntimeError(
                "Gemini temporal comparison failed: "
                f"{error}"
            ) from error

        if not response.text:

            raise RuntimeError(
                "Gemini did not return a comparison."
            )

        return response.text.strip()

    # =========================================================
    # RUN COMPLETE TOOL
    # =========================================================

    def run(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:

        user_question = (
            parameters.get("question")
            or parameters.get("query")
        )

        # -----------------------------------------------------
        # FIRST CHECK FOR CHANGE ANALYSIS DEPENDENCY
        # -----------------------------------------------------

        change_data = self._get_change_analysis(
            parameters
        )

        if change_data:

            before_path = change_data.get(
                "before_image"
            )

            after_path = change_data.get(
                "after_image"
            )

            if (
                before_path
                and after_path
                and Path(before_path).exists()
                and Path(after_path).exists()
            ):

                caption = self._compare_images(
                    before_path=before_path,
                    after_path=after_path,
                    user_question=user_question,
                    change_data=change_data,
                )

                before_image = Image.open(
                    before_path
                ).convert("RGB")

                after_image = Image.open(
                    after_path
                ).convert("RGB")

                return {
                    "tool": self.name,
                    "status": "success",
                    "analysis_mode": (
                        "temporal_comparison"
                    ),
                    "caption": caption,
                    "before_image": before_path,
                    "after_image": after_path,
                    "before_width": before_image.size[0],
                    "before_height": before_image.size[1],
                    "after_width": after_image.size[0],
                    "after_height": after_image.size[1],
                    "change_evidence": {
                        "change_percentage": (
                            change_data.get(
                                "change_percentage"
                            )
                        ),
                        "mean_ndvi_before": (
                            change_data.get(
                                "mean_ndvi_before"
                            )
                        ),
                        "mean_ndvi_after": (
                            change_data.get(
                                "mean_ndvi_after"
                            )
                        ),
                        "ndvi_change": (
                            change_data.get(
                                "ndvi_change"
                            )
                        ),
                        "vegetation_status": (
                            change_data.get(
                                "vegetation_status"
                            )
                        ),
                    },
                    "before_sentinel": (
                        change_data.get(
                            "before_sentinel"
                        )
                    ),
                    "after_sentinel": (
                        change_data.get(
                            "after_sentinel"
                        )
                    ),
                }

        # -----------------------------------------------------
        # FALLBACK: SINGLE IMAGE ANALYSIS
        # -----------------------------------------------------

        image_path, sentinel_metadata = (
            self._get_image_path(
                parameters
            )
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        width, height = image.size

        caption = self._analyze_image(
            image_path=image_path,
            user_question=user_question,
        )

        result = {
            "tool": self.name,
            "status": "success",
            "analysis_mode": "single_image",
            "caption": caption,
            "image": image_path,
            "width": width,
            "height": height,
        }

        if sentinel_metadata:

            result["sentinel"] = {
                "product_id": (
                    sentinel_metadata.get(
                        "product_id"
                    )
                ),
                "datetime": (
                    sentinel_metadata.get(
                        "datetime"
                    )
                ),
                "cloud_cover": (
                    sentinel_metadata.get(
                        "cloud_cover"
                    )
                ),
            }

        return result