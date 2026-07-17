"""Application configuration via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven configuration.

    Values are loaded from environment variables or a ``.env`` file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "Patient Management Service"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/patient_db"

    # --- CORS ---
    cors_origins: list[str] = ["*"]

    # --- Logging ---
    # LOG_LEVEL: DEBUG | INFO | WARNING | ERROR | CRITICAL  (default: INFO)
    # LOG_FORMAT: "text" (colorized, human-readable) | "json" (structured, for prod)
    log_level: str = "INFO"
    log_format: str = "text"


settings = Settings()
