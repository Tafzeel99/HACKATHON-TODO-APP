"""Environment configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database - Neon PostgreSQL
    database_url: str

    # Better Auth
    better_auth_secret: str
    better_auth_url: str = "https://auth.example.com"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Environment
    environment: str = "development"

    # JWT Settings
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7

    @property
    def async_database_url(self) -> str:
        """Convert postgres:// to postgresql+asyncpg:// for async support."""
        url = self.database_url
        # SQLite URLs are already in async format
        if url.startswith("sqlite"):
            return url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
