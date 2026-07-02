from __future__ import annotations

import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from dotenv import load_dotenv

from contextos.core.config import Settings, reset_settings_cache
from tests.support import configure_test_database_environment

ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
PYTEST_TEMP_DIR = Path(__file__).resolve().parents[1] / "tmp" / f"pytest-{os.getpid()}"

load_dotenv(ROOT_ENV_FILE, override=False)
load_dotenv(BACKEND_ENV_FILE, override=False)
PYTEST_TEMP_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("TMP", str(PYTEST_TEMP_DIR))
os.environ.setdefault("TEMP", str(PYTEST_TEMP_DIR))
os.environ.setdefault("TMPDIR", str(PYTEST_TEMP_DIR))
tempfile.tempdir = str(PYTEST_TEMP_DIR)
configure_test_database_environment()


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
