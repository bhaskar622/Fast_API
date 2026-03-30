from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost/fast_complaint_manage_system"
    secret_key: str = "fast_AsGQxNbb8hpggAH9xgnmPBYe12t9VXpQ"
    algorithm: str = "HS256"
    # access_token_expire_minutes: int = 30
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
