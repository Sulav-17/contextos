from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, Final, cast
from urllib.parse import unquote, urlparse
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from alembic.config import Config
from contextos.infrastructure.tenant_context import set_tenant_context

USER_A: Final = UUID("10000000-0000-4000-8000-000000000001")
USER_B: Final = UUID("10000000-0000-4000-8000-000000000002")
RLS_TEST_USERS: Final = (USER_A, USER_B)
RLS_TEST_EMAILS: Final = ("security-a@example.test", "security-b@example.test")


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.fail(f"{name} is required for PostgreSQL-backed RLS security tests.")
    return value


def database_username(database_url: str) -> str:
    parsed = urlparse(database_url)
    if not parsed.username:
        pytest.fail(f"{database_url!r} must include an explicit database username.")
    return unquote(parsed.username)


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
async def runtime_engine(migrated_database: None) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(required_env("CONTEXTOS_DATABASE_URL"), pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


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


@pytest.fixture
async def seeded_tenants(
    migration_engine: AsyncEngine,
) -> AsyncGenerator[tuple[UUID, UUID]]:
    async with migration_engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        await connection.execute(
            text(
                """
                DELETE FROM user_preferences
                WHERE user_id = ANY(:user_ids)
                """
            ),
            {"user_ids": [str(user_id) for user_id in RLS_TEST_USERS]},
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
                "user_ids": [str(user_id) for user_id in RLS_TEST_USERS],
                "emails": list(RLS_TEST_EMAILS),
            },
        )
        await connection.execute(
            text(
                """
                INSERT INTO users (id, email, role, status)
                VALUES
                  (:user_a, 'security-a@example.test', 'user', 'active'),
                  (:user_b, 'security-b@example.test', 'user', 'active')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"user_a": str(USER_A), "user_b": str(USER_B)},
        )
        for user_id, greeting_mode in ((USER_A, "full"), (USER_B, "direct")):
            await connection.execute(
                text("SELECT set_config('request.jwt.claim.sub', :user_id, true)"),
                {"user_id": str(user_id)},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO user_preferences (
                      user_id,
                      greeting_mode,
                      motion_mode,
                      theme_mode,
                      welcome_completed
                    )
                    VALUES (:user_id, :greeting_mode, 'system', 'dark', false)
                    ON CONFLICT (user_id) DO UPDATE
                    SET greeting_mode = EXCLUDED.greeting_mode,
                        motion_mode = EXCLUDED.motion_mode,
                        theme_mode = EXCLUDED.theme_mode,
                        welcome_completed = EXCLUDED.welcome_completed
                    """
                ),
                {"user_id": str(user_id), "greeting_mode": greeting_mode},
            )
    try:
        yield USER_A, USER_B
    finally:
        async with migration_engine.begin() as connection:
            await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
            await connection.execute(
                text(
                    """
                    DELETE FROM user_preferences
                    WHERE user_id = ANY(:user_ids)
                    """
                ),
                {"user_ids": [str(user_id) for user_id in RLS_TEST_USERS]},
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
                    "user_ids": [str(user_id) for user_id in RLS_TEST_USERS],
                    "emails": list(RLS_TEST_EMAILS),
                },
            )


async def tenant_session(engine: AsyncEngine, actor_id: UUID) -> AsyncSession:
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = factory()
    await session.begin()
    await set_tenant_context(session, actor_id, "user")
    return session


@pytest.mark.asyncio
async def test_tenant_can_read_own_rows(
    runtime_engine: AsyncEngine,
    seeded_tenants: tuple[UUID, UUID],
) -> None:
    user_a, _ = seeded_tenants
    session = await tenant_session(runtime_engine, user_a)
    try:
        user_rows = (
            await session.execute(text("SELECT id FROM users ORDER BY email"))
        ).scalars().all()
        preference_rows = (
            await session.execute(text("SELECT user_id FROM user_preferences ORDER BY user_id"))
        ).scalars().all()
    finally:
        await session.rollback()
        await session.close()

    assert user_rows == [user_a]
    assert preference_rows == [user_a]


@pytest.mark.asyncio
async def test_tenant_cannot_read_another_tenants_rows(
    runtime_engine: AsyncEngine,
    seeded_tenants: tuple[UUID, UUID],
) -> None:
    user_a, user_b = seeded_tenants
    session = await tenant_session(runtime_engine, user_a)
    try:
        other_user = (
            await session.execute(
                text("SELECT id FROM users WHERE id = :user_b"),
                {"user_b": str(user_b)},
            )
        ).scalar_one_or_none()
        other_preferences = (
            await session.execute(
                text("SELECT user_id FROM user_preferences WHERE user_id = :user_b"),
                {"user_b": str(user_b)},
            )
        ).scalar_one_or_none()
    finally:
        await session.rollback()
        await session.close()

    assert other_user is None
    assert other_preferences is None


@pytest.mark.asyncio
async def test_tenant_cannot_update_or_delete_another_tenants_rows(
    runtime_engine: AsyncEngine,
    migration_engine: AsyncEngine,
    seeded_tenants: tuple[UUID, UUID],
) -> None:
    user_a, user_b = seeded_tenants
    session = await tenant_session(runtime_engine, user_a)
    try:
        update_result = cast(
            CursorResult[Any],
            await session.execute(
                text(
                    """
                    UPDATE user_preferences
                    SET greeting_mode = 'minimized'
                    WHERE user_id = :user_b
                    """
                ),
                {"user_b": str(user_b)},
            ),
        )
        assert update_result.rowcount == 0

        with pytest.raises(DBAPIError):
            await session.execute(
                text("DELETE FROM user_preferences WHERE user_id = :user_b"),
                {"user_b": str(user_b)},
            )
    finally:
        await session.rollback()
        await session.close()

    async with migration_engine.connect() as connection:
        result = await connection.execute(
            text("SELECT greeting_mode FROM user_preferences WHERE user_id = :user_b"),
            {"user_b": str(user_b)},
        )
        assert result.scalar_one() == "direct"


@pytest.mark.asyncio
async def test_missing_tenant_context_fails_closed(
    runtime_engine: AsyncEngine,
    seeded_tenants: tuple[UUID, UUID],
) -> None:
    user_a, _ = seeded_tenants
    async with runtime_engine.begin() as connection:
        visible_users = (await connection.execute(text("SELECT count(*) FROM users"))).scalar_one()
        visible_preferences = (
            await connection.execute(text("SELECT count(*) FROM user_preferences"))
        ).scalar_one()
        update_result = await connection.execute(
            text(
                """
                UPDATE user_preferences
                SET greeting_mode = 'minimized'
                WHERE user_id = :user_a
                """
            ),
            {"user_a": str(user_a)},
        )

    assert visible_users == 0
    assert visible_preferences == 0
    assert update_result.rowcount == 0


@pytest.mark.asyncio
async def test_runtime_database_role_cannot_bypass_rls(
    runtime_engine: AsyncEngine,
    migration_engine: AsyncEngine,
    seeded_tenants: tuple[UUID, UUID],
) -> None:
    runtime_role = database_username(required_env("CONTEXTOS_DATABASE_URL"))
    async with migration_engine.connect() as connection:
        bypass_rls = (
            await connection.execute(
                text("SELECT rolbypassrls FROM pg_roles WHERE rolname = :runtime_role"),
                {"runtime_role": runtime_role},
            )
        ).scalar_one()

    async with runtime_engine.begin() as connection:
        await connection.execute(text("SET LOCAL row_security = off"))
        with pytest.raises(DBAPIError):
            await connection.execute(text("SELECT count(*) FROM users"))

    assert bypass_rls is False


@pytest.mark.asyncio
async def test_normal_application_sessions_use_runtime_role(
    runtime_engine: AsyncEngine,
    seeded_tenants: tuple[UUID, UUID],
) -> None:
    runtime_role = database_username(required_env("CONTEXTOS_DATABASE_URL"))
    migration_role = database_username(required_env("CONTEXTOS_MIGRATION_DATABASE_URL"))

    async with runtime_engine.connect() as connection:
        current_user = (await connection.execute(text("SELECT current_user"))).scalar_one()

    assert current_user == runtime_role
    assert current_user != migration_role
