from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Final
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import command
from alembic.config import Config
from contextos.auth.errors import AUTHENTICATION_REQUIRED, INVALID_AUTHENTICATION
from contextos.auth.jwt import AuthenticationError
from contextos.auth.principal import Principal
from contextos.core.config import Settings
from contextos.infrastructure.database import DatabaseResource
from contextos.main import create_app

PUBLIC_USER: Final = UUID("20000000-0000-4000-8000-000000000001")
REQUEST_INPUT_USER: Final = UUID("20000000-0000-4000-8000-000000000002")
MALICIOUS_USER: Final = UUID("20000000-0000-4000-8000-000000000099")
PROVISIONING_TEST_USERS: Final = (PUBLIC_USER, REQUEST_INPUT_USER, MALICIOUS_USER)
PROVISIONING_TEST_EMAILS: Final = (
    "verified.user@example.test",
    "principal.user@example.test",
    "attacker@example.test",
    "unauthenticated@example.test",
)


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.fail(f"{name} is required for PostgreSQL-backed provisioning tests.")
    return value


def build_alembic_config() -> Config:
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[2] / "alembic"))
    config.set_main_option("sqlalchemy.url", required_env("CONTEXTOS_MIGRATION_DATABASE_URL"))
    return config


@pytest.fixture(scope="session")
def migrated_database() -> None:
    required_env("CONTEXTOS_DATABASE_URL")
    required_env("CONTEXTOS_MIGRATION_DATABASE_URL")
    required_env("POSTGRES_APP_USER")
    command.upgrade(build_alembic_config(), "head")


@pytest.fixture
async def migration_engine(migrated_database: None) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        required_env("CONTEXTOS_MIGRATION_DATABASE_URL"),
        pool_pre_ping=True,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


async def delete_test_users(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        await connection.execute(
            text(
                """
                DELETE FROM user_preferences
                WHERE user_id = ANY(:user_ids)
                """
            ),
            {"user_ids": [str(user_id) for user_id in PROVISIONING_TEST_USERS]},
        )
        await connection.execute(
            text(
                """
                DELETE FROM users
                WHERE id = ANY(:user_ids)
                   OR email = ANY(:emails)
                """
            ),
            {
                "user_ids": [str(user_id) for user_id in PROVISIONING_TEST_USERS],
                "emails": list(PROVISIONING_TEST_EMAILS),
            },
        )


@pytest.fixture(autouse=True)
async def clean_provisioning_test_users(
    migration_engine: AsyncEngine,
) -> AsyncGenerator[None]:
    await delete_test_users(migration_engine)
    try:
        yield
    finally:
        await delete_test_users(migration_engine)


class FakeRedisResource:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def start(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def health_check(self, timeout_seconds: float) -> bool:
        return True


class FakeAuthProvider:
    async def verify_authorization_header(self, authorization: str | None) -> Principal:
        if authorization == "Bearer public-user":
            return Principal(PUBLIC_USER, "Verified.User@Example.TEST", None)
        if authorization == "Bearer request-input-user":
            return Principal(REQUEST_INPUT_USER, "Principal.User@Example.TEST", None)
        if authorization is None:
            raise AuthenticationError(AUTHENTICATION_REQUIRED.code)
        raise AuthenticationError(INVALID_AUTHENTICATION.code)


def build_app() -> TestClient:
    settings = Settings(
        application_name="contextos-api",
        application_version="0.1.0",
        environment="test",
        log_level="INFO",
        log_format="json",
        database_url=required_env("CONTEXTOS_DATABASE_URL"),
        migration_database_url=required_env("CONTEXTOS_MIGRATION_DATABASE_URL"),
        redis_url="redis://127.0.0.1:6379/0",
        readiness_timeout_seconds=3,
    )
    app = create_app(
        settings=settings,
        database_resource_factory=DatabaseResource,
        redis_resource_factory=FakeRedisResource,
        auth_provider_factory=lambda settings: FakeAuthProvider(),
    )
    return TestClient(app)


async def read_user_row(engine: AsyncEngine, user_id: UUID) -> dict[str, object] | None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        result = await connection.execute(
            text("SELECT id, email, role, status FROM users WHERE id = :user_id"),
            {"user_id": str(user_id)},
        )
        row = result.mappings().one_or_none()
    return dict(row) if row is not None else None


async def count_users_by_email(engine: AsyncEngine, email: str) -> int:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        result = await connection.execute(
            text("SELECT count(*) FROM users WHERE email = :email"),
            {"email": email},
        )
    return int(result.scalar_one())


@pytest.mark.asyncio
async def test_first_authenticated_access_provisions_one_local_user(
    migration_engine: AsyncEngine,
) -> None:
    with build_app() as client:
        response = client.get("/api/v1/me", headers={"Authorization": "Bearer public-user"})

    assert response.status_code == 200
    assert response.json()["id"] == str(PUBLIC_USER)
    row = await read_user_row(migration_engine, PUBLIC_USER)
    assert row == {
        "id": PUBLIC_USER,
        "email": "verified.user@example.test",
        "role": "user",
        "status": "active",
    }


@pytest.mark.asyncio
async def test_repeat_authenticated_access_is_idempotent(
    migration_engine: AsyncEngine,
) -> None:
    with build_app() as client:
        first = client.get("/api/v1/me", headers={"Authorization": "Bearer public-user"})
        second = client.get("/api/v1/me", headers={"Authorization": "Bearer public-user"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert await count_users_by_email(migration_engine, "verified.user@example.test") == 1


@pytest.mark.asyncio
async def test_provisioning_uses_verified_principal_not_request_input(
    migration_engine: AsyncEngine,
) -> None:
    with build_app() as client:
        response = client.get(
            f"/api/v1/me?user_id={MALICIOUS_USER}&email=attacker@example.test",
            headers={
                "Authorization": "Bearer request-input-user",
                "X-User-ID": str(MALICIOUS_USER),
                "X-Email": "attacker@example.test",
            },
        )

    assert response.status_code == 200
    row = await read_user_row(migration_engine, REQUEST_INPUT_USER)
    assert row is not None
    assert row["email"] == "principal.user@example.test"
    assert await read_user_row(migration_engine, MALICIOUS_USER) is None
    assert await count_users_by_email(migration_engine, "attacker@example.test") == 0


@pytest.mark.asyncio
async def test_unauthenticated_access_cannot_provision_user(
    migration_engine: AsyncEngine,
) -> None:
    with build_app() as client:
        response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert await count_users_by_email(migration_engine, "unauthenticated@example.test") == 0
