from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from contextos.core.config import Settings
from contextos.infrastructure.database import DatabaseResource
from contextos.infrastructure.redis_client import RedisResource
from tests.support import ensure_test_database, required_test_database_url


@pytest.fixture(scope="module", autouse=True)
def isolated_test_database() -> None:
    ensure_test_database()


def build_integration_settings() -> Settings:
    database_url = required_test_database_url(
        "CONTEXTOS_TEST_DATABASE_URL",
        "CONTEXTOS_DATABASE_URL",
    )
    redis_url = os.environ.get("CONTEXTOS_REDIS_URL")
    if not redis_url:
        pytest.fail("Integration tests require CONTEXTOS_REDIS_URL.")

    return Settings(
        application_name="contextos-api",
        application_version="0.1.0",
        environment="test",
        log_level="INFO",
        log_format="json",
        database_url=database_url,
        redis_url=redis_url,
        readiness_timeout_seconds=3,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_select_one() -> None:
    resource = DatabaseResource(build_integration_settings())
    await resource.start()
    try:
        assert await resource.health_check(timeout_seconds=3) is True
    finally:
        await resource.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_ping() -> None:
    resource = RedisResource(build_integration_settings())
    await resource.start()
    try:
        assert await resource.health_check(timeout_seconds=3) is True
    finally:
        await resource.close()


@pytest.mark.integration
def test_application_ready_with_live_services() -> None:
    from contextos.main import create_app

    app = create_app(settings=build_integration_settings())
    with TestClient(app) as client:
        health_response = client.get("/health")
        assert health_response.status_code == 200

        ready_response = client.get("/ready")
        assert ready_response.status_code == 200
        assert ready_response.json() == {
            "status": "ready",
            "checks": {"database": "ok", "redis": "ok"},
        }
        assert "X-Request-ID" in ready_response.headers
