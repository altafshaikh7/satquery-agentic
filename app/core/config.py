from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # --------------------------------------------------
    # APP SETTINGS
    # --------------------------------------------------

    app_name: str = "SatQuery AI"
    app_version: str = "1.0.0"
    debug: bool = True

    # --------------------------------------------------
    # LLM SETTINGS
    # --------------------------------------------------

    llm_provider: str = "gemini"

    google_api_key: str | None = None
    gemini_api_key: str | None = None

    gemini_model: str = "gemini-3.6-flash"

    # --------------------------------------------------
    # COPERNICUS DATA SPACE SETTINGS
    # --------------------------------------------------

    cdse_client_id: str | None = None
    cdse_client_secret: str | None = None

    cdse_token_url: str = (
        "https://identity.dataspace.copernicus.eu/auth/"
        "realms/CDSE/protocol/openid-connect/token"
    )

    cdse_catalog_url: str = (
        "https://sh.dataspace.copernicus.eu/catalog/v1/search"
    )

    cdse_process_url: str = (
        "https://sh.dataspace.copernicus.eu/api/v1/process"
    )

    # --------------------------------------------------
    # ENV CONFIG
    # --------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()