from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://devuser:devpass@localhost:5432/orrin_dev"

    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"

    # Application
    APP_NAME: str = "Orrin Dev"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra environment variables
    )


settings = Settings()
