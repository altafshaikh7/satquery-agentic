from google import genai

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not configured"
            )

        self.client = genai.Client(
            api_key=settings.google_api_key
        )

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        return response.text