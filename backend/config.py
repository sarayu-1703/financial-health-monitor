"""
config.py — Loads all settings from .env via pydantic-settings.
Zero hardcoded values anywhere else in the codebase.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App metadata
    app_name: str = "Fyntwin Financial Health Monitor"
    app_version: str = "1.0.0"
    app_env: str = "development"

    # PostgreSQL
    database_url: str

    # Anthropic / Agno
    anthropic_api_key: str
    agno_model: str = "claude-3-5-haiku-20241022"


# Singleton — import `settings` everywhere
settings = Settings()
