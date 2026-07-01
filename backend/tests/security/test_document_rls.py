from __future__ import annotations

import hashlib
import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, Final, cast
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from alembic.config import Config
from contextos.infrastructure.tenant_context import set_tenant_context

USER_A: Final = UUID("40000000-0000-4000-8000-000000000001")
USER_B: Final = UUID("40000000-0000-4000-8000-000000000002")
DOCUMENT_A: Final = UUID("41000000-0000-4000-8000-000000000001")
DOCUMENT_B: Final = UUID("41000000-0000-4000-8000-000000000002")
CONVERSATION_A: Final = UUID("42000000-0000-4000-8000-000000000001")
CONVERSATION_B: Final = UUID("42000000-0000-4000-8000-000000000002")


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.fail(f"{name} is required for PostgreSQL-backed document RLS tests.")
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


async def cleanup(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'worker', true)"))
        await connection.execute(
            text("DELETE FROM documents WHERE user_id = ANY(:user_ids)"),
            {"user_ids": [str(USER_A), str(USER_B)]},
        )
        await connection.execute(
            text("SELECT set_config('request.jwt.claim.sub', :user_a, true)"),
            {"user_a": str(USER_A)},
        )
        await connection.execute(
            text("DELETE FROM conversations WHERE user_id = :user_a"), {"user_a": str(USER_A)}
        )
        await connection.execute(
            text("DELETE FROM usage_counters WHERE user_id = :user_a"), {"user_a": str(USER_A)}
        )
        await connection.execute(
            text("SELECT set_config('request.jwt.claim.sub', :user_b, true)"),
            {"user_b": str(USER_B)},
        )
        await connection.execute(
            text("DELETE FROM conversations WHERE user_id = :user_b"), {"user_b": str(USER_B)}
        )
        await connection.execute(
            text("DELETE FROM usage_counters WHERE user_id = :user_b"), {"user_b": str(USER_B)}
        )
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        await connection.execute(
            text("DELETE FROM users WHERE id = ANY(:user_ids)"),
            {"user_ids": [str(USER_A), str(USER_B)]},
        )


@pytest.fixture
async def seeded_document_tenants(migration_engine: AsyncEngine) -> AsyncGenerator[None]:
    await cleanup(migration_engine)
    async with migration_engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        await connection.execute(
            text(
                """
                INSERT INTO users (id, email, role, status)
                VALUES
                  (:user_a, 'document-security-a@example.test', 'user', 'active'),
                  (:user_b, 'document-security-b@example.test', 'user', 'active')
                """
            ),
            {"user_a": str(USER_A), "user_b": str(USER_B)},
        )
        await connection.execute(text("SELECT set_config('app.actor_role', 'worker', true)"))
        for user_id, document_id, filename in (
            (USER_A, DOCUMENT_A, "a.pdf"),
            (USER_B, DOCUMENT_B, "b.pdf"),
        ):
            await connection.execute(
                text(
                    """
                    INSERT INTO documents (
                      id, user_id, original_filename, storage_key, mime_type, size_bytes,
                      checksum_sha256, status, page_count
                    )
                    VALUES (
                      :document_id, :user_id, :filename, :storage_key, 'application/pdf',
                      128, repeat('a', 64), 'ready', 1
                    )
                    """
                ),
                {
                    "document_id": str(document_id),
                    "user_id": str(user_id),
                    "filename": filename,
                    "storage_key": f"{document_id}.pdf",
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO document_chunks (
                      document_id, user_id, chunk_index, page_number, content, character_count,
                      content_sha256
                    )
                    VALUES (
                      :document_id, :user_id, 0, 1, 'safe test chunk', 15, :content_sha256
                    )
                    """
                ),
                {
                    "document_id": str(document_id),
                    "user_id": str(user_id),
                    "content_sha256": hashlib.sha256(b"safe test chunk").hexdigest(),
                },
            )
        for user_id, conversation_id, document_id in (
            (USER_A, CONVERSATION_A, DOCUMENT_A),
            (USER_B, CONVERSATION_B, DOCUMENT_B),
        ):
            await connection.execute(
                text("SELECT set_config('request.jwt.claim.sub', :user_id, true)"),
                {"user_id": str(user_id)},
            )
            message_id = (
                await connection.execute(
                    text(
                        """
                        INSERT INTO conversations (id, user_id, title)
                        VALUES (:conversation_id, :user_id, 'RLS')
                        RETURNING id
                        """
                    ),
                    {"conversation_id": str(conversation_id), "user_id": str(user_id)},
                )
            ).scalar_one()
            assistant_id = (
                await connection.execute(
                    text(
                        """
                        INSERT INTO messages (conversation_id, user_id, role, content, status)
                        VALUES (:conversation_id, :user_id, 'assistant', 'Answer', 'completed')
                        RETURNING id
                        """
                    ),
                    {"conversation_id": str(message_id), "user_id": str(user_id)},
                )
            ).scalar_one()
            chunk_id = (
                await connection.execute(
                    text(
                        """
                        SELECT id FROM document_chunks
                        WHERE document_id = :document_id AND user_id = :user_id
                        """
                    ),
                    {"document_id": str(document_id), "user_id": str(user_id)},
                )
            ).scalar_one()
            await connection.execute(
                text(
                    """
                    INSERT INTO message_citations (
                      message_id, user_id, document_id, chunk_id, page_number,
                      citation_index, excerpt
                    )
                    VALUES (
                      :message_id, :user_id, :document_id, :chunk_id, 1, 1, 'safe excerpt'
                    )
                    """
                ),
                {
                    "message_id": str(assistant_id),
                    "user_id": str(user_id),
                    "document_id": str(document_id),
                    "chunk_id": str(chunk_id),
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO usage_counters (user_id, period_type, period_start, message_count)
                    VALUES (:user_id, 'daily', CURRENT_DATE, 1)
                    """
                ),
                {"user_id": str(user_id)},
            )
    try:
        yield
    finally:
        await cleanup(migration_engine)


async def tenant_session(engine: AsyncEngine, actor_id: UUID) -> AsyncSession:
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = factory()
    await session.begin()
    await set_tenant_context(session, actor_id, "user")
    return session


@pytest.mark.asyncio
async def test_document_tables_are_tenant_isolated(
    runtime_engine: AsyncEngine,
    seeded_document_tenants: None,
) -> None:
    session = await tenant_session(runtime_engine, USER_A)
    try:
        documents = (await session.execute(text("SELECT id FROM documents"))).scalars().all()
        chunks = (
            (await session.execute(text("SELECT document_id FROM document_chunks"))).scalars().all()
        )
        conversations = (
            (await session.execute(text("SELECT id FROM conversations"))).scalars().all()
        )
        messages = (await session.execute(text("SELECT user_id FROM messages"))).scalars().all()
        citations = (
            (await session.execute(text("SELECT document_id FROM message_citations")))
            .scalars()
            .all()
        )
        usage = (await session.execute(text("SELECT user_id FROM usage_counters"))).scalars().all()
        update_result = cast(
            CursorResult[Any],
            await session.execute(
                text("UPDATE documents SET status = 'failed' WHERE id = :document_b"),
                {"document_b": str(DOCUMENT_B)},
            ),
        )
        delete_result = cast(
            CursorResult[Any],
            await session.execute(
                text("DELETE FROM document_chunks WHERE document_id = :document_b"),
                {"document_b": str(DOCUMENT_B)},
            ),
        )
    finally:
        await session.rollback()
        await session.close()

    assert documents == [DOCUMENT_A]
    assert chunks == [DOCUMENT_A]
    assert conversations == [CONVERSATION_A]
    assert messages == [USER_A]
    assert citations == [DOCUMENT_A]
    assert usage == [USER_A]
    assert update_result.rowcount == 0
    assert delete_result.rowcount == 0


@pytest.mark.asyncio
async def test_document_tables_missing_tenant_context_fails_closed(
    runtime_engine: AsyncEngine,
    seeded_document_tenants: None,
) -> None:
    async with runtime_engine.begin() as connection:
        visible_documents = (
            await connection.execute(text("SELECT count(*) FROM documents"))
        ).scalar_one()
        visible_chunks = (
            await connection.execute(text("SELECT count(*) FROM document_chunks"))
        ).scalar_one()
        visible_conversations = (
            await connection.execute(text("SELECT count(*) FROM conversations"))
        ).scalar_one()
        visible_messages = (
            await connection.execute(text("SELECT count(*) FROM messages"))
        ).scalar_one()
        visible_citations = (
            await connection.execute(text("SELECT count(*) FROM message_citations"))
        ).scalar_one()
        visible_usage = (
            await connection.execute(text("SELECT count(*) FROM usage_counters"))
        ).scalar_one()
        update_result = await connection.execute(
            text("UPDATE documents SET status = 'failed' WHERE id = :document_a"),
            {"document_a": str(DOCUMENT_A)},
        )

    assert visible_documents == 0
    assert visible_chunks == 0
    assert visible_conversations == 0
    assert visible_messages == 0
    assert visible_citations == 0
    assert visible_usage == 0
    assert update_result.rowcount == 0
