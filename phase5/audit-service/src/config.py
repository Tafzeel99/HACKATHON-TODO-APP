"""Configuration for the Audit Service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Audit service settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "audit-service"
    log_level: str = "INFO"
    dapr_http_port: int = 3500
    app_port: int = 8003
    backend_app_id: str = "backend-service"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()