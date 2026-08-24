from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SatQuery AI"
    app_version: str = "1.0.0"
    debug: bool = True

    llm_provider: str = "mock"

    openai_api_key: str | None = None

    google_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()