from app.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    def generate(self, prompt: str) -> str:
        return f"Mock LLM response for: {prompt}"