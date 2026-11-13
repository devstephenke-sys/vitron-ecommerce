"""Core application configuration."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Development-only JWT secret. >=32 bytes for HS256; production MUST set
# AUTH_SECRET_KEY (enforced by the validator below).
DEV_AUTH_SECRET = "vitron-dev-secret-change-me-0123456789abcdef"  # noqa: S105


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["local", "development", "staging", "production", "test"] = "local"
    database_url: str = Field(
        default="postgresql+asyncpg://vitron:vitron@localhost:5433/vitron",
        description="SQLAlchemy async connection string (asyncpg driver).",
    )
    # NoDecode keeps the raw comma-separated string so the validator below
    # can split it (pydantic-settings would otherwise JSON-decode list fields).
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:3001"]
    )
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # Auth/JWT settings. The default secret is for local development only;
    # production must override AUTH_SECRET_KEY (enforced below).
    auth_secret_key: str = DEV_AUTH_SECRET  # noqa: S105
    access_token_ttl_seconds: int = 900  # 15 minutes
    refresh_token_ttl_seconds: int = 2_592_000  # 30 days
    password_reset_ttl_seconds: int = 3_600  # 1 hour

    @model_validator(mode="after")
    def _reject_default_secret_in_production(self) -> "Settings":
        if self.is_production and self.auth_secret_key == DEV_AUTH_SECRET:
            raise ValueError("AUTH_SECRET_KEY must be set to a unique secret in production")
        return self

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Allow CORS_ORIGINS to be provided as a comma-separated string."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
