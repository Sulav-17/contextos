from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

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
