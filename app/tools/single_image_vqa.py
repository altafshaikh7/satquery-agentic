import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

from app.tools.base import BaseTool


load_dotenv()


class SingleImageVQATool(BaseTool):
    name = "single_image_vqa"

    description = (
        "Answer a user's remote sensing question about a "
        "single satellite or aerial image using Gemini Vision."
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

    def _load_image(
        self,
        image_path: str,
    ) -> Image.Image:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        return Image.open(path).convert("RGB")

    def _analyze_image(
        self,
        image: Image.Image,
        question: str,
    ) -> str:
        prompt = f"""
You are an expert Earth Observation and remote sensing analyst.

Analyze the provided satellite or aerial image and answer
the user's question accurately.

User question:
{question}

Instructions:
- Base your answer only on visually observable information.
- Focus on relevant remote sensing features such as vegetation,
  agriculture, water bodies, urban areas, infrastructure,
  land cover, terrain, and visible spatial patterns when relevant.
- Do not invent place names, dates, events, or measurements.
- Clearly mention uncertainty when something cannot be determined
  reliably from the image alone.
- Do not claim exact classifications without sufficient visual evidence.
- Give a direct and useful answer to the user's specific question.
"""

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                prompt,
                image,
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini did not return an answer."
            )

        return response.text.strip()

    def run(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:

        image_urls = parameters.get("image_urls", [])

        question = (
            parameters.get("question")
            or parameters.get("query")
            or ""
        )

        if not image_urls:
            raise ValueError(
                "Single image VQA requires at least one image URL"
            )

        if not question.strip():
            raise ValueError(
                "Single image VQA requires a question or query"
            )

        image_path = image_urls[0]

        image = self._load_image(
            image_path
        )

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
            "width": image.width,
            "height": image.height,
            "model": "gemini-3.6-flash",
        }