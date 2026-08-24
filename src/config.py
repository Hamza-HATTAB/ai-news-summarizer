import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings configuration using Pydantic.
    """
    groq_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    default_timeframe: str = "daily"
    default_model: str = "llama-3.3-70b-versatile"
    output_dir: str = "./news_reports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def validate_keys() -> bool:
        return bool(self.groq_api_key or os.getenv("GROQ_API_KEY"))


settings = Settings()
