"""
Configuration settings for the FastAPI backend.

Environment variables:
- DATABASE_URL: PostgreSQL connection string (Neon)
- JWT_SECRET: Secret key for JWT token verification
- BETTER_AUTH_SECRET: Secret key for Better Auth (same as JWT_SECRET)
- CORS_ORIGINS: Comma-separated list of allowed origins
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/todoapp"

    # Authentication
    jwt_secret: str = "your-secret-key-change-in-production"
    better_auth_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # CORS (comma-separated string)
    cors_origins: str = "http://localhost:3000"

    # API
    api_prefix: str = "/api"
    debug: bool = True

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields
    )


# Global settings instance
settings = Settings()
