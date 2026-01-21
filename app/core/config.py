from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

# Insecure default key - used to detect if user forgot to set SECRET_KEY
_INSECURE_DEFAULT_KEY = "change-this-to-a-random-secret-key-in-production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://devuser:devpass@localhost:5432/orrin_dev"

    # Security
    SECRET_KEY: str = _INSECURE_DEFAULT_KEY

    # Application
    APP_NAME: str = "Orrin Dev"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra environment variables
    )

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """Ensure SECRET_KEY is set to a secure value in production."""
        if not self.DEBUG and self.SECRET_KEY == _INSECURE_DEFAULT_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a secure value in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters for adequate security."
            )
        return self


settings = Settings()
