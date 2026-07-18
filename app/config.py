"""Application configuration via pydantic-settings."""

from __future__ import annotations

from pydantic import Field
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
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    # --- CORS ---
    cors_origins: list[str] = ["*"]

    # --- JWT (shared with identity-service for local token verification) ---
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"

    # --- Logging ---
    # LOG_LEVEL: DEBUG | INFO | WARNING | ERROR | CRITICAL  (default: INFO)
    # LOG_FORMAT: "text" (colorized, human-readable) | "json" (structured, for prod)
    log_level: str = "INFO"
    log_format: str = "text"


settings = Settings()
