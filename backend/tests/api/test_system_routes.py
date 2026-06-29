from __future__ import annotations

import os
from collections.abc import Callable

from fastapi import FastAPI
from fastapi.testclient import TestClient

from contextos.core.config import Settings

os.environ.setdefault(
    "CONTEXTOS_DATABASE_URL",
    "postgresql+asyncpg://test-user:test-password@db.example/contextos_test",
)
os.environ.setdefault("CONTEXTOS_REDIS_URL", "redis://redis.example:6379/0")

from contextos.main import create_app


class FakeDatabaseResource:
    def __init__(self, healthy: bool = True) -> None:
        self.healthy = healthy
        self.health_calls = 0

    async def start(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def health_check(self, timeout_seconds: float) -> bool:
        self.health_calls += 1
        return self.healthy


class FakeRedisResource:
    def __init__(self, healthy: bool = True) -> None:
        self.healthy = healthy
        self.health_calls = 0

    async def start(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def health_check(self, timeout_seconds: float) -> bool:
        self.health_calls += 1
        return self.healthy


def build_app(
    make_settings: Callable[..., Settings],
    database_healthy: bool = True,
    redis_healthy: bool = True,
) -> tuple[FastAPI, FakeDatabaseResource, FakeRedisResource]:
    database = FakeDatabaseResource(healthy=database_healthy)
    redis = FakeRedisResource(healthy=redis_healthy)
    app = create_app(
        settings=make_settings(),
        database_resource_factory=lambda settings: database,
        redis_resource_factory=lambda settings: redis,
    )
    return app, database, redis


def test_health_route_returns_liveness_payload(
    make_settings: Callable[..., Settings],
) -> None:
    app, _, _ = build_app(make_settings)
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "contextos-api",
            "version": "0.1.0",
        }


def test_health_route_does_not_call_infrastructure(
    make_settings: Callable[..., Settings],
) -> None:
    app, database, redis = build_app(make_settings)
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert database.health_calls == 0
        assert redis.health_calls == 0


def test_ready_route_returns_healthy_response(
    make_settings: Callable[..., Settings],
) -> None:
    app, _, _ = build_app(make_settings)
    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ready",
            "checks": {"database": "ok", "redis": "ok"},
        }


def test_ready_route_returns_database_failure(
    make_settings: Callable[..., Settings],
) -> None:
    app, _, _ = build_app(make_settings, database_healthy=False)
    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json() == {
            "status": "not_ready",
            "checks": {"database": "unavailable", "redis": "ok"},
        }


def test_ready_route_returns_redis_failure(
    make_settings: Callable[..., Settings],
) -> None:
    app, _, _ = build_app(make_settings, redis_healthy=False)
    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json() == {
            "status": "not_ready",
            "checks": {"database": "ok", "redis": "unavailable"},
        }


def test_ready_route_returns_both_failures(
    make_settings: Callable[..., Settings],
) -> None:
    app, _, _ = build_app(make_settings, database_healthy=False, redis_healthy=False)
    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json() == {
            "status": "not_ready",
            "checks": {"database": "unavailable", "redis": "unavailable"},
        }


def test_ready_route_does_not_leak_connection_details(
    make_settings: Callable[..., Settings],
) -> None:
    app, _, _ = build_app(make_settings, database_healthy=False)
    with TestClient(app) as client:
        response = client.get("/ready")
        body = response.text
        assert "postgresql+asyncpg://" not in body
        assert "redis://" not in body
        assert "db.example" not in body
        assert "test-password" not in body


def test_request_id_response_behavior(
    make_settings: Callable[..., Settings],
) -> None:
    app, _, _ = build_app(make_settings)
    with TestClient(app) as client:
        safe_response = client.get("/health", headers={"X-Request-ID": "safe-id_123"})
        assert safe_response.headers["X-Request-ID"] == "safe-id_123"

        generated_response = client.get(
            "/health",
            headers={"X-Request-ID": "bad value with spaces"},
        )
        generated_request_id = generated_response.headers["X-Request-ID"]
        assert generated_request_id != "bad value with spaces"
        assert len(generated_request_id) == 36
