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
    Download a real Sentinel-2 satellite image from Copernicus
    and analyze it using Gemini Vision.
    """

    name = "scene_caption"

    description = (
        "Download a real Sentinel-2 satellite image from Copernicus "
        "and analyze it using Gemini Vision."
    )

    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Add it to your .env file."
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
        """
        Get an image from either:

        1. Existing local image path
        2. Geographic bounding box, which downloads
           a real Sentinel-2 image
        """

        image_urls = parameters.get("image_urls", [])

        # -----------------------------------------------------
        # OPTION 1: EXISTING LOCAL IMAGE
        # -----------------------------------------------------

        if image_urls:
            if not isinstance(image_urls, list):
                raise ValueError(
                    "'image_urls' must be a list."
                )

            image_path = Path(image_urls[0])

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Image file not found: {image_urls[0]}"
                )

            return str(image_path), None

        # -----------------------------------------------------
        # OPTION 2: DOWNLOAD FROM BBOX
        # -----------------------------------------------------

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
                    output_path="data/latest_scene_sentinel2.png",
                    lookback_days=180,
                    max_cloud_coverage=80.0,
                )
            )

            return result["image_path"], result

        raise ValueError(
            "Provide either 'image_urls' or 'bbox'."
        )

    # =========================================================
    # ANALYZE IMAGE WITH GEMINI
    # =========================================================

    def _analyze_image(
        self,
        image_path: str,
        user_question: str | None = None,
    ) -> str:
        """
        Send the real satellite image to Gemini Vision.
        """

        image = Image.open(
            image_path
        ).convert("RGB")

        prompt = """
You are an expert Earth Observation and remote sensing analyst.

Analyze this real Sentinel-2 satellite image carefully.

Describe only what is visually observable.

Consider the following:

- Vegetation and forest cover
- Agricultural land and crop patterns
- Urban or built-up areas
- Roads or visible linear infrastructure
- Rivers, lakes, reservoirs, or other water bodies
- Terrain and land-use patterns

Important rules:

- Do not invent precise place names.
- Do not invent events or facts that cannot be determined
  from the image.
- Clearly distinguish observations from uncertainty.
- Do not claim exact measurements unless visible data
  supports them.
- Provide a concise but useful Earth Observation analysis.
"""

        if user_question:
            prompt += (
                "\n\nThe user specifically asks:\n"
                f"{user_question}"
            )

        try:
            response = (
                self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        prompt,
                        image,
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.2,
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
    # RUN COMPLETE TOOL
    # =========================================================

    def run(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run the complete pipeline.

        Option 1: Analyze existing image

        {
            "image_urls": [
                "data/best_sentinel2.png"
            ],
            "question": "Analyze land use"
        }


        Option 2: Download and analyze real Sentinel-2 image

        {
            "bbox": [
                74.10,
                15.80,
                74.30,
                16.00
            ],
            "question": "Analyze land use and water bodies"
        }
        """

        # -----------------------------------------------------
        # GET USER QUESTION
        # -----------------------------------------------------

        user_question = (
            parameters.get("question")
            or parameters.get("query")
        )

        # -----------------------------------------------------
        # GET OR DOWNLOAD IMAGE
        # -----------------------------------------------------

        image_path, sentinel_metadata = (
            self._get_image_path(parameters)
        )

        # -----------------------------------------------------
        # GET IMAGE DIMENSIONS
        # -----------------------------------------------------

        image = Image.open(
            image_path
        ).convert("RGB")

        width, height = image.size

        # -----------------------------------------------------
        # ANALYZE IMAGE WITH GEMINI
        # -----------------------------------------------------

        caption = self._analyze_image(
            image_path=image_path,
            user_question=user_question,
        )

        # -----------------------------------------------------
        # BUILD RESPONSE
        # -----------------------------------------------------

        result = {
            "tool": self.name,
            "status": "success",
            "caption": caption,
            "image": image_path,
            "width": width,
            "height": height,
        }

        # -----------------------------------------------------
        # ADD SENTINEL METADATA IF IMAGE WAS DOWNLOADED
        # -----------------------------------------------------

        if sentinel_metadata:
            result["sentinel"] = {
                "product_id": sentinel_metadata.get(
                    "product_id"
                ),
                "datetime": sentinel_metadata.get(
                    "datetime"
                ),
                "cloud_cover": sentinel_metadata.get(
                    "cloud_cover"
                ),
            }

        return result