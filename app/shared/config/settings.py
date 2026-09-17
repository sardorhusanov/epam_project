from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "EPAM Project API"
    APP_ENVIRONMENT: Literal["development", "testing", "staging", "production"] = (
        "development"
    )
    DEBUG: bool = False
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/epam_project"
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, gt=0)
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=15, gt=0)

    @field_validator("DATABASE_URL")
    @classmethod
    def require_async_database_driver(cls, value: str) -> str:
        if not value.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError("DATABASE_URL must use an async SQLAlchemy driver")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
