"""Configuration for the Notification Service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Notification service settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "notification-service"
    log_level: str = "INFO"
    dapr_http_port: int = 3500
    app_port: int = 8001


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
