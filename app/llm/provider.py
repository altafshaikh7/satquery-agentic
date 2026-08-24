from app.core.config import settings
from app.llm.mock_provider import MockLLMProvider


def get_llm_provider():
    if settings.llm_provider.lower() == "mock":
        return MockLLMProvider()

    if settings.llm_provider.lower() == "openai":
        from app.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )