from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["local", "test", "staging", "production"]
LogFormat = Literal["json", "console"]

ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"
BACKEND_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CONTEXTOS_",
        env_file=(ROOT_ENV_FILE, BACKEND_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    application_name: str = "contextos-api"
    application_version: str = "0.1.0"
    environment: AppEnvironment = "local"
    log_level: str = "INFO"
    log_format: LogFormat = "console"
    database_url: SecretStr = Field(repr=False)
    redis_url: SecretStr = Field(repr=False)
    readiness_timeout_seconds: float = Field(default=3.0, gt=0, le=30)

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in ALLOWED_LOG_LEVELS:
            raise ValueError("log_level must be one of DEBUG, INFO, WARNING, ERROR, or CRITICAL.")
        return normalized

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if not secret.startswith("postgresql+asyncpg://"):
            raise ValueError("database_url must start with postgresql+asyncpg://")
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if not secret.startswith("redis://"):
            raise ValueError("redis_url must start with redis://")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
