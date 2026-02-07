"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str

    # JWT Authentication Secret (minimum 32 characters)
    JWT_SECRET: str
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000"

    # Debug Mode
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
