from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest

from contextos.core.config import Settings, reset_settings_cache


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    reset_settings_cache()
    yield
    reset_settings_cache()


@pytest.fixture
def make_settings() -> Callable[..., Settings]:
    def _make_settings(**overrides: object) -> Settings:
        base_settings: dict[str, object] = {
            "application_name": "contextos-api",
            "application_version": "0.1.0",
            "environment": "test",
            "log_level": "INFO",
            "log_format": "json",
            "database_url": "postgresql+asyncpg://test-user:test-password@db.example/contextos_test",
            "redis_url": "redis://redis.example:6379/0",
            "readiness_timeout_seconds": 2.0,
        }
        base_settings.update(overrides)
        return Settings.model_validate(base_settings)

    return _make_settings
