from openai import OpenAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return response.output_text