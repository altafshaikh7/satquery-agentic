from app.core.config import settings
from app.llm.mock_provider import MockLLMProvider


def get_llm_provider():
    provider = settings.llm_provider.lower()

    if provider == "mock":
        return MockLLMProvider()

    if provider == "openai":
        from app.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()

    if provider == "gemini":
        from app.llm.gemini_provider import GeminiProvider

        return GeminiProvider()

    raise ValueError(
        f"Unsupported LLM provider: "
        f"{settings.llm_provider}"
    )