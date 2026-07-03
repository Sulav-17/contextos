from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

import contextos.core.config as config_module
from contextos.core.config import Settings, get_settings, reset_settings_cache


def test_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXTOS_DATABASE_URL", "postgresql+asyncpg://user:secret@db/contextos")
    monkeypatch.setenv("CONTEXTOS_REDIS_URL", "redis://redis:6379/0")
    monkeypatch.setenv("CONTEXTOS_ENVIRONMENT", "test")
    monkeypatch.setenv("CONTEXTOS_LOG_FORMAT", "json")
    settings = Settings()

    assert settings.environment == "test"
    assert settings.log_format == "json"
    assert settings.database_url.get_secret_value().startswith("postgresql+asyncpg://")


def test_settings_require_connection_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXTOS_DATABASE_URL", raising=False)
    monkeypatch.delenv("CONTEXTOS_REDIS_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("CONTEXTOS_ENVIRONMENT", "dev"),
        ("CONTEXTOS_LOG_FORMAT", "text"),
        ("CONTEXTOS_READINESS_TIMEOUT_SECONDS", "0"),
    ],
)
def test_settings_validate_invalid_values(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
) -> None:
    monkeypatch.setenv("CONTEXTOS_DATABASE_URL", "postgresql+asyncpg://user:secret@db/contextos")
    monkeypatch.setenv("CONTEXTOS_REDIS_URL", "redis://redis:6379/0")
    monkeypatch.setenv(field, value)

    with pytest.raises(ValidationError):
        Settings()


def test_settings_repr_hides_connection_secrets(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        database_url="postgresql+asyncpg://user:super-secret@db.example/contextos",
        redis_url="redis://:another-secret@redis.example:6379/0",
    )

    representation = repr(settings)
    assert "super-secret" not in representation
    assert "another-secret" not in representation
    assert "postgresql+asyncpg://" not in representation
    assert "redis://" not in representation


def test_settings_cache_can_be_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXTOS_DATABASE_URL", "postgresql+asyncpg://user:secret@db/contextos")
    monkeypatch.setenv("CONTEXTOS_REDIS_URL", "redis://redis:6379/0")
    first = get_settings()

    monkeypatch.setenv("CONTEXTOS_LOG_LEVEL", "DEBUG")
    reset_settings_cache()
    second = get_settings()

    assert first is not second
    assert second.log_level == "DEBUG"


def test_production_settings_require_safe_external_services(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        environment="production",
        database_url="postgresql+asyncpg://app:secret@aws-1-ca-central-1.pooler.supabase.com/contextos",
        migration_database_url="postgresql+asyncpg://migration:secret@aws-1-ca-central-1.pooler.supabase.com/contextos",
        redis_url="redis://cache.example.com:6379/0",
        supabase_url="https://project.supabase.co",
        supabase_jwt_issuer="https://project.supabase.co/auth/v1",
        supabase_jwks_url="https://project.supabase.co/auth/v1/.well-known/jwks.json",
        supabase_secret_key="server-secret",
        frontend_url="https://contextos.example.com",
        document_storage_backend="supabase",
        supabase_storage_bucket="contextos-private-documents",
        llm_provider="gemini",
        embedding_provider="gemini",
        ai_provider_api_key="provider-secret",
    )

    assert settings.environment == "production"
    assert settings.document_storage_backend == "supabase"


@pytest.mark.parametrize(
    "database_host",
    [
        "aws-1-ca-central-1.pooler.supabase.com",
        "db.project-ref.supabase.co",
    ],
)
def test_production_settings_accept_public_dns_database_hosts(
    make_settings: Callable[..., Settings],
    database_host: str,
) -> None:
    settings = make_settings(
        environment="production",
        database_url=f"postgresql+asyncpg://app:secret@{database_host}/contextos",
        migration_database_url=f"postgresql+asyncpg://migration:secret@{database_host}/contextos",
        redis_url="redis://cache.example.com:6379/0",
        supabase_url="https://project.supabase.co",
        supabase_jwt_issuer="https://project.supabase.co/auth/v1",
        supabase_jwks_url="https://project.supabase.co/auth/v1/.well-known/jwks.json",
        supabase_secret_key="server-secret",
        frontend_url="https://contextos.example.com",
        document_storage_backend="supabase",
        supabase_storage_bucket="contextos-private-documents",
        llm_provider="gemini",
        embedding_provider="gemini",
        ai_provider_api_key="provider-secret",
    )

    assert settings.database_url.get_secret_value().endswith(f"@{database_host}/contextos")


@pytest.mark.parametrize(
    "database_host",
    [
        "aws-1-ca-central-1.pooler.supabase.com",
        "db.project-ref.supabase.co",
    ],
)
def test_production_dns_database_hosts_do_not_call_ip_address(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
    database_host: str,
) -> None:
    def fail_if_called(hostname: str) -> object:
        raise AssertionError(f"ip_address should not be called for {hostname}")

    monkeypatch.setattr(config_module, "ip_address", fail_if_called)

    assert Settings._hostname_is_unsafe_literal_ip(database_host) is False
    Settings._validate_not_local_database_url(
        f"postgresql+asyncpg://app:secret@{database_host}/contextos",
        "database_url",
    )
    settings = make_settings(
        environment="production",
        database_url=f"postgresql+asyncpg://app:secret@{database_host}/contextos",
        migration_database_url=f"postgresql+asyncpg://migration:secret@{database_host}/contextos",
        redis_url="redis://cache.example.com:6379/0",
        supabase_url="https://project.supabase.co",
        supabase_jwt_issuer="https://project.supabase.co/auth/v1",
        supabase_jwks_url="https://project.supabase.co/auth/v1/.well-known/jwks.json",
        supabase_secret_key="server-secret",
        frontend_url="https://contextos.example.com",
        document_storage_backend="supabase",
        supabase_storage_bucket="contextos-private-documents",
        llm_provider="gemini",
        embedding_provider="gemini",
        ai_provider_api_key="provider-secret",
    )

    assert settings.environment == "production"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"database_url": "postgresql+asyncpg://app:secret@localhost/contextos"}, "database"),
        ({"database_url": "postgresql+asyncpg://app:secret@127.0.0.1/contextos"}, "database"),
        ({"database_url": "postgresql+asyncpg://app:secret@[::1]/contextos"}, "database"),
        ({"database_url": "postgresql+asyncpg://app:secret@10.0.0.10/contextos"}, "database"),
        ({"redis_url": "redis://localhost:6379/0"}, "redis_url"),
        ({"redis_url": "redis://10.0.0.10:6379/0"}, "redis_url"),
        ({"frontend_url": "http://contextos.example.com"}, "frontend_url"),
        ({"document_storage_backend": "local"}, "document storage"),
        ({"llm_provider": "fake"}, "fake AI"),
        ({"embedding_provider": "fake"}, "fake AI"),
        ({"ai_provider_api_key": ""}, "AI provider API key"),
        ({"supabase_storage_bucket": ""}, "storage bucket"),
    ],
)
def test_production_settings_reject_unsafe_values(
    make_settings: Callable[..., Settings],
    overrides: dict[str, object],
    message: str,
) -> None:
    values: dict[str, object] = {
        "environment": "production",
        "database_url": "postgresql+asyncpg://app:secret@db.example.com/contextos",
        "migration_database_url": "postgresql+asyncpg://migration:secret@db.example.com/contextos",
        "redis_url": "redis://cache.example.com:6379/0",
        "supabase_url": "https://project.supabase.co",
        "supabase_jwt_issuer": "https://project.supabase.co/auth/v1",
        "supabase_jwks_url": "https://project.supabase.co/auth/v1/.well-known/jwks.json",
        "supabase_secret_key": "server-secret",
        "frontend_url": "https://contextos.example.com",
        "document_storage_backend": "supabase",
        "supabase_storage_bucket": "contextos-private-documents",
        "llm_provider": "gemini",
        "embedding_provider": "gemini",
        "ai_provider_api_key": "provider-secret",
    }
    values.update(overrides)

    with pytest.raises(ValidationError, match=message):
        make_settings(**values)
