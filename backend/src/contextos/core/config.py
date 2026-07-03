from __future__ import annotations

from functools import lru_cache
from ipaddress import ip_address
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["local", "test", "staging", "production"]
LogFormat = Literal["json", "console"]
DocumentStorageBackend = Literal["local", "supabase"]

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
    migration_database_url: SecretStr | None = Field(default=None, repr=False)
    redis_url: SecretStr = Field(repr=False)
    readiness_timeout_seconds: float = Field(default=3.0, gt=0, le=30)
    supabase_url: str = ""
    supabase_jwt_issuer: str = ""
    supabase_jwt_audience: str = "authenticated"
    supabase_jwks_url: str = ""
    supabase_allowed_jwt_algorithms: tuple[str, ...] = ("ES256", "RS256")
    supabase_jwks_cache_ttl_seconds: int = Field(default=300, gt=0, le=3600)
    supabase_jwt_clock_skew_seconds: int = Field(default=30, ge=0, le=120)
    supabase_secret_key: SecretStr | None = Field(default=None, repr=False)
    frontend_url: str = "http://localhost:3000"
    beta_max_users: int = Field(default=3, gt=0, le=3)
    document_storage_backend: DocumentStorageBackend = "local"
    document_storage_root: Path = Path("data/private-documents")
    supabase_storage_bucket: str = ""
    supabase_storage_path_prefix: str = "documents"
    document_max_per_user: int = Field(default=10, gt=0, le=100)
    document_max_pdf_size_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    document_max_total_size_bytes: int = Field(default=50 * 1024 * 1024, gt=0)
    document_max_pages: int = Field(default=100, gt=0, le=1000)
    document_chunk_size: int = Field(default=1800, gt=100, le=10000)
    document_chunk_overlap: int = Field(default=200, ge=0, le=2000)
    document_queue_name: str = "contextos-ingestion"
    llm_provider: Literal["fake", "gemini"] = "fake"
    llm_model: str = "gemini-2.5-flash"
    embedding_provider: Literal["fake", "gemini"] = "fake"
    embedding_model: str = "text-embedding-004"
    ai_provider_api_key: SecretStr | None = Field(default=None, repr=False)
    ai_provider_timeout_seconds: float = Field(default=12.0, gt=0, le=60)
    ai_provider_max_retries: int = Field(default=2, ge=0, le=5)
    embedding_dimension: int = Field(default=768, gt=0, le=4096)
    retrieval_top_k: int = Field(default=5, gt=0, le=20)
    retrieval_similarity_threshold: float = Field(default=0.72, ge=0, le=1)
    retrieval_max_context_characters: int = Field(default=9000, gt=1000, le=30000)
    memory_retrieval_top_k: int = Field(default=4, gt=0, le=10)
    memory_retrieval_similarity_threshold: float = Field(default=0.72, ge=0, le=1)
    memory_retrieval_max_context_characters: int = Field(default=1800, gt=200, le=6000)
    ai_daily_message_limit: int = Field(default=20, gt=0, le=10000)
    ai_monthly_message_limit: int = Field(default=200, gt=0, le=100000)

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

    @field_validator("migration_database_url")
    @classmethod
    def validate_migration_database_url(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return value
        secret = value.get_secret_value()
        if not secret.startswith("postgresql+asyncpg://"):
            raise ValueError("migration_database_url must start with postgresql+asyncpg://")
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if not secret.startswith("redis://"):
            raise ValueError("redis_url must start with redis://")
        return value

    @field_validator("supabase_allowed_jwt_algorithms", mode="before")
    @classmethod
    def validate_algorithms(cls, value: str | tuple[str, ...] | list[str]) -> tuple[str, ...]:
        algorithms = (
            tuple(part.strip().upper() for part in value.split(","))
            if isinstance(value, str)
            else tuple(value)
        )
        if not algorithms:
            raise ValueError("at least one JWT algorithm must be allowed")
        if any(algorithm.startswith("HS") for algorithm in algorithms):
            raise ValueError("symmetric JWT algorithms are not allowed")
        if not set(algorithms).issubset({"ES256", "RS256"}):
            raise ValueError("allowed JWT algorithms must be ES256 or RS256")
        return algorithms

    @model_validator(mode="after")
    def validate_auth_configuration(self) -> Settings:
        if not self.supabase_jwks_url and self.supabase_url:
            self.supabase_jwks_url = (
                self.supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
            )

        if self.environment == "production":
            if not self.supabase_url or not self.supabase_jwt_issuer or not self.supabase_jwks_url:
                raise ValueError("production requires Supabase URL, issuer, and JWKS URL")
            for field_name, value in (
                ("supabase_url", self.supabase_url),
                ("supabase_jwt_issuer", self.supabase_jwt_issuer),
                ("supabase_jwks_url", self.supabase_jwks_url),
                ("frontend_url", self.frontend_url),
            ):
                parsed = urlparse(value)
                if parsed.scheme != "https" or "*" in value:
                    raise ValueError(f"production {field_name} must be an exact HTTPS URL")
            if not self._secret_has_value(self.supabase_secret_key):
                raise ValueError("production invitations require a Supabase server secret key")
            if not self._secret_has_value(self.ai_provider_api_key):
                raise ValueError("production requires an AI provider API key")
            if self.llm_provider == "fake" or self.embedding_provider == "fake":
                raise ValueError("production cannot use fake AI providers")
            if self.document_storage_backend != "supabase":
                raise ValueError("production document storage must use the supabase backend")
            if not self.supabase_storage_bucket:
                raise ValueError("production requires a Supabase storage bucket")
            self._validate_not_local_database_url(
                self.database_url.get_secret_value(), "database_url"
            )
            if self.migration_database_url is not None:
                self._validate_not_local_database_url(
                    self.migration_database_url.get_secret_value(), "migration_database_url"
                )
            self._validate_not_local_redis_url(self.redis_url.get_secret_value())
        return self

    @staticmethod
    def _secret_has_value(value: SecretStr | None) -> bool:
        return bool(value and value.get_secret_value().strip())

    @staticmethod
    def _validate_not_local_database_url(value: str, field_name: str) -> None:
        parsed = urlparse(value.replace("postgresql+asyncpg://", "postgresql://", 1))
        local_hosts = {"", "localhost", "127.0.0.1", "::1", "postgres"}
        if parsed.hostname in local_hosts or parsed.path.endswith("_test"):
            raise ValueError(f"production {field_name} cannot point at local or test database")
        if Settings._hostname_is_unsafe_literal_ip(parsed.hostname):
            raise ValueError(f"production {field_name} cannot point at local or test database")

    @staticmethod
    def _validate_not_local_redis_url(value: str) -> None:
        parsed = urlparse(value)
        if parsed.hostname in {"", "localhost", "127.0.0.1", "::1", "redis"}:
            raise ValueError("production redis_url cannot point at local Redis")
        if Settings._hostname_is_unsafe_literal_ip(parsed.hostname):
            raise ValueError("production redis_url cannot point at local Redis")

    @staticmethod
    def _hostname_is_unsafe_literal_ip(hostname: str | None) -> bool:
        if hostname is None:
            return False
        try:
            address = ip_address(hostname)
        except ValueError:
            return False
        return (
            address.is_loopback
            or address.is_private
            or address.is_link_local
            or address.is_reserved
            or address.is_unspecified
            or address.is_multicast
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
