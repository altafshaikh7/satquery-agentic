import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, UnidentifiedImageError

from app.tools.base import BaseTool


load_dotenv()


class SingleImageVQATool(BaseTool):
    """
    Analyze a single user-provided satellite or aerial image.

    The analysis is restricted to information that can be
    supported by the visible pixels in the provided image.
    """

    name = "single_image_vqa"

    description = (
        "Answer a user's remote sensing question about a single "
        "satellite or aerial image using Gemini Vision, while "
        "strictly separating direct observations from uncertainty."
    )

    def __init__(self) -> None:
        self.gemini_api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not self.gemini_api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY is missing. "
                "Add one API key to your .env file."
            )

        self.gemini_model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )

        self.client = genai.Client(
            api_key=self.gemini_api_key
        )

    # =========================================================
    # LOAD IMAGE
    # =========================================================

    def _load_image(
        self,
        image_path: str,
    ) -> Image.Image:
        """
        Load and validate the uploaded image.
        """

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Image path is not a file: {image_path}"
            )

        try:
            with Image.open(path) as image:
                image.verify()

            with Image.open(path) as image:
                return image.convert("RGB")

        except UnidentifiedImageError as error:
            raise ValueError(
                f"Invalid or unsupported image file: {image_path}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                f"Failed to load image: {error}"
            ) from error

    # =========================================================
    # ANALYZE IMAGE
    # =========================================================

    def _analyze_image(
        self,
        image: Image.Image,
        question: str,
    ) -> str:
        """
        Send the actual uploaded image to Gemini Vision.

        The prompt is designed to reduce hallucination and
        prevent unsupported assumptions.
        """

        prompt = f"""
You are an expert Earth Observation and remote sensing analyst.

You are analyzing ONE actual satellite or aerial image provided
with this request.

USER QUESTION:
{question}

Your primary requirement is ACCURACY AND EVIDENCE.

STRICT RULES:

1. Analyze ONLY the image provided in this request.

2. Treat every statement as an observation only if it is supported
   by visible pixels or clearly visible spatial patterns.

3. Do NOT guess hidden or unclear objects.

4. Do NOT invent:
   - city names
   - country names
   - place names
   - GPS coordinates
   - acquisition dates
   - events
   - object identities
   - exact land-use classes
   - exact measurements
   - population
   - building counts
   - road names
   - temporal changes

5. Do NOT identify an exact location from visual appearance alone.
   If the user asks where the image was taken, explain that the
   exact city or location cannot be reliably determined from image
   pixels alone unless geospatial metadata is separately provided.

6. Do NOT convert a possibility into a fact.

   BAD:
   "There is a tennis court."

   BETTER:
   "A rectangular light-colored area is visible, but its exact
   function cannot be confirmed from this image alone."

7. Do NOT claim vehicles, people, crops, building types, sports
   facilities, industrial facilities, or other small objects unless
   they are clearly distinguishable at the available resolution.

8. If the image resolution is insufficient for a requested detail,
   explicitly say:
   "This cannot be determined reliably at the available image
   resolution."

9. Distinguish between:

   DIRECTLY OBSERVED:
   Features clearly visible in the image.

   LIKELY / INTERPRETED:
   A cautious interpretation based on visible patterns.
   Use this section only when useful and clearly label it as
   interpretation.

   NOT DETERMINABLE:
   Information that cannot be reliably concluded from this image.

10. For remote sensing analysis, focus only on relevant visible
    features such as:
    - built-up areas
    - buildings
    - roads
    - vegetation
    - agricultural field patterns
    - bare soil
    - water bodies
    - terrain patterns
    - visible linear infrastructure
    - spatial distribution and land-cover patterns

11. A single image does NOT prove change over time.
    Do not claim increase, decrease, deforestation, construction,
    damage, flooding, or any temporal change unless comparison
    imagery or temporal data is provided.

12. Answer the user's actual question directly.
    Do not provide unrelated analysis.

13. Before producing the final answer, silently check every factual
    statement against the visible image. Remove statements that are
    speculative, too detailed for the resolution, or unsupported.

OUTPUT FORMAT:

### Directly Observed
- Only clearly visible facts relevant to the question.

### Interpretation / Uncertainty
- Clearly separate cautious interpretations from direct observations.
- If no reliable interpretation is possible, say so.

### Cannot Be Determined
- List important information requested by the user that cannot be
  reliably determined from this image alone.

Keep the answer concise, evidence-based, and honest about uncertainty.
"""

        try:
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=[
                    prompt,
                    image,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                ),
            )

        except Exception as error:
            raise RuntimeError(
                f"Gemini image analysis failed: {error}"
            ) from error

        if not response.text:
            raise RuntimeError(
                "Gemini did not return an answer."
            )

        return response.text.strip()

    # =========================================================
    # RUN TOOL
    # =========================================================

    def run(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run single-image visual question answering.
        """

        image_urls = parameters.get(
            "image_urls",
            [],
        )

        question = (
            parameters.get("question")
            or parameters.get("query")
            or ""
        )

        if not isinstance(image_urls, list):
            raise ValueError(
                "image_urls must be a list."
            )

        if not image_urls:
            raise ValueError(
                "Single image VQA requires at least one image."
            )

        if not isinstance(question, str):
            raise ValueError(
                "Question or query must be a string."
            )

        question = question.strip()

        if not question:
            raise ValueError(
                "Single image VQA requires a question or query."
            )

        image_path = str(
            image_urls[0]
        ).strip()

        if not image_path:
            raise ValueError(
                "The provided image path is empty."
            )

        # Load the actual uploaded image.
        image = self._load_image(
            image_path
        )

        width, height = image.size

        # Analyze the actual image.
        answer = self._analyze_image(
            image=image,
            question=question,
        )

        return {
            "tool": self.name,
            "status": "success",
            "query": question,
            "answer": answer,
            "image": image_path,
            "width": width,
            "height": height,
            "model": self.gemini_model,
        }