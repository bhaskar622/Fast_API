# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Reads from environment variables automatically.
    'DATABASE_URL' env var → settings.database_url
    Falls back to defaults if env var is not set.
    """
    database_url: str = "postgresql+asyncpg://postgres:password@localhost/fast_project_manage_system"
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = False

    class Config:
        # Also reads from a .env file automatically
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()  # Cache the settings — don't re-read env vars on every call
def get_settings() -> Settings:
    return Settings()
