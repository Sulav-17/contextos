from __future__ import annotations

import hashlib
import os
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from typing import Any, Final, cast
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from alembic.config import Config
from contextos.auth.errors import AUTHENTICATION_REQUIRED, INVALID_AUTHENTICATION
from contextos.auth.jwt import AuthenticationError
from contextos.auth.principal import Principal
from contextos.core.config import Settings
from contextos.domain.ai import build_embedding_provider
from contextos.domain.chat import RetrievedChunk, retrieve_chunks, vector_literal
from contextos.infrastructure.database import DatabaseResource
from contextos.main import create_app

USER_A: Final = UUID("32000000-0000-4000-8000-000000000001")
USER_B: Final = UUID("32000000-0000-4000-8000-000000000002")
DOCUMENT_A: Final = UUID("33000000-0000-4000-8000-000000000001")
DOCUMENT_B: Final = UUID("33000000-0000-4000-8000-000000000002")
DOCUMENT_OTHER: Final = UUID("33000000-0000-4000-8000-000000000003")


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.fail(f"{name} is required for conversation API tests.")
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
        if authorization == "Bearer user-a":
            return Principal(USER_A, "chat-a@example.test", None)
        if authorization == "Bearer user-b":
            return Principal(USER_B, "chat-b@example.test", None)
        if authorization is None:
            raise AuthenticationError(AUTHENTICATION_REQUIRED.code)
        raise AuthenticationError(INVALID_AUTHENTICATION.code)


@pytest.fixture
def build_client(
    clean_conversation_rows: None,
) -> Callable[..., TestClient]:
    def _build_client(**overrides: object) -> TestClient:
        settings = Settings.model_validate(
            {
                "application_name": "contextos-api",
                "application_version": "0.1.0",
                "environment": "test",
                "log_level": "INFO",
                "log_format": "json",
                "database_url": required_env("CONTEXTOS_DATABASE_URL"),
                "migration_database_url": required_env("CONTEXTOS_MIGRATION_DATABASE_URL"),
                "redis_url": "redis://127.0.0.1:6379/0",
                "embedding_provider": "fake",
                "llm_provider": "fake",
                "retrieval_similarity_threshold": 0.2,
                **overrides,
            }
        )
        return TestClient(
            create_app(
                settings=settings,
                database_resource_factory=DatabaseResource,
                redis_resource_factory=FakeRedisResource,
                auth_provider_factory=lambda settings: FakeAuthProvider(),
            )
        )

    return _build_client


async def cleanup(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'worker', true)"))
        await connection.execute(
            text("DELETE FROM documents WHERE user_id = ANY(:user_ids)"),
            {"user_ids": [str(USER_A), str(USER_B)]},
        )
        await connection.execute(text("SELECT set_config('app.actor_role', 'user', true)"))
        await connection.execute(
            text("DELETE FROM conversations WHERE user_id = ANY(:user_ids)"),
            {"user_ids": [str(USER_A), str(USER_B)]},
        )
        await connection.execute(
            text("DELETE FROM usage_counters WHERE user_id = ANY(:user_ids)"),
            {"user_ids": [str(USER_A), str(USER_B)]},
        )
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        await connection.execute(
            text("DELETE FROM users WHERE id = ANY(:user_ids)"),
            {"user_ids": [str(USER_A), str(USER_B)]},
        )


@pytest.fixture
async def clean_conversation_rows(migration_engine: AsyncEngine) -> AsyncGenerator[None]:
    await cleanup(migration_engine)
    try:
        yield
    finally:
        await cleanup(migration_engine)


async def seed_document(
    engine: AsyncEngine,
    *,
    settings: Settings,
    user_id: UUID,
    document_id: UUID,
    filename: str,
    content: str,
    embedding: list[float] | None = None,
) -> None:
    provider = build_embedding_provider(settings)
    vector = embedding or (await provider.embed([content]))[0]
    async with engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        await connection.execute(
            text(
                """
                INSERT INTO users (id, email, role, status)
                VALUES (:user_id, :email, 'user', 'active')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"user_id": str(user_id), "email": f"{user_id}@example.test"},
        )
        await connection.execute(text("SELECT set_config('app.actor_role', 'worker', true)"))
        await connection.execute(
            text(
                """
                INSERT INTO documents (
                  id, user_id, original_filename, storage_key, mime_type, size_bytes,
                  checksum_sha256, status, page_count, extracted_character_count
                )
                VALUES (
                  :document_id, :user_id, :filename, :storage_key, 'application/pdf',
                  128, repeat('a', 64), 'ready', 1, :character_count
                )
                """
            ),
            {
                "document_id": str(document_id),
                "user_id": str(user_id),
                "filename": filename,
                "storage_key": f"{document_id}.pdf",
                "character_count": len(content),
            },
        )
        await connection.execute(
            text(
                """
                INSERT INTO document_chunks (
                  document_id, user_id, chunk_index, page_number, content, character_count,
                  content_sha256, embedding, embedding_provider, embedding_model,
                  embedding_dimension, embedding_created_at
                )
                VALUES (
                  :document_id, :user_id, 0, 1, :content, :character_count,
                  :content_sha256, CAST(:embedding AS vector), :embedding_provider,
                  :embedding_model, :embedding_dimension, now()
                )
                """
            ),
            {
                "document_id": str(document_id),
                "user_id": str(user_id),
                "content": content,
                "character_count": len(content),
                "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
                "embedding": vector_literal(vector),
                "embedding_provider": provider.provider,
                "embedding_model": provider.model,
                "embedding_dimension": provider.dimension,
            },
        )


def fixed_vector(first: float, second: float) -> list[float]:
    vector = [0.0] * 768
    vector[0] = first
    vector[1] = second
    return vector


@pytest.mark.asyncio
async def test_conversation_question_persists_answer_and_citations(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client() as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="orbit.pdf",
            content="Quiet Orbit stores private PDFs with citation backed answers.",
        )
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_B,
            filename="other.pdf",
            content="Gardens use soil and sunlight.",
        )
        created = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Research"},
        )
        conversation_id = created.json()["id"]
        answer = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What does Quiet Orbit store?", "document_ids": [str(DOCUMENT_A)]},
        )
        detail = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers={"Authorization": "Bearer user-a"},
        )

    assert created.status_code == 201
    assert answer.status_code == 200
    assert answer.json()["usage"]["daily"]["used"] == 1
    assert answer.json()["message"]["citations"][0]["document_name"] == "orbit.pdf"
    assert len(detail.json()["messages"]) == 2


@pytest.mark.asyncio
async def test_conversations_are_tenant_isolated_and_fallback_on_weak_evidence(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client(retrieval_similarity_threshold=0.99) as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="tenant-a.pdf",
            content="Only tenant A can retrieve this passage.",
        )
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_B,
            document_id=DOCUMENT_OTHER,
            filename="tenant-b.pdf",
            content="Tenant B content must not appear.",
        )
        created = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Isolation"},
        )
        conversation_id = created.json()["id"]
        cross_tenant = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers={"Authorization": "Bearer user-b"},
        )
        fallback = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What is not in the files?"},
        )

    assert cross_tenant.status_code == 404
    assert fallback.status_code == 200
    assert fallback.json()["evidence_status"] == "insufficient_evidence"
    assert fallback.json()["message"]["citations"] == []


@pytest.mark.asyncio
async def test_retrieval_threshold_is_honored(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    async def collect_chunks(settings: Settings) -> list[RetrievedChunk]:
        factory = async_sessionmaker(
            migration_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with factory() as session:
            await session.begin()
            return await retrieve_chunks(
                session,
                user_id=USER_A,
                query_embedding=fixed_vector(1.0, 0.0),
                settings=settings,
                document_ids=[],
            )

    with build_client(retrieval_similarity_threshold=0.55, retrieval_top_k=3) as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="threshold.pdf",
            content="Threshold document",
            embedding=fixed_vector(0.6, 0.8),
        )
        chunks = await collect_chunks(settings)

    assert len(chunks) == 1

    with build_client(retrieval_similarity_threshold=0.65, retrieval_top_k=3) as client:
        settings = cast(Any, client.app).state.settings
        chunks = await collect_chunks(settings)

    assert chunks == []


def test_usage_limits_are_enforced(build_client: Callable[..., TestClient]) -> None:
    with build_client(ai_daily_message_limit=1, ai_monthly_message_limit=1) as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Limits"},
        ).json()
        first = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "No documents yet."},
        )
        second = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "Still no documents."},
        )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "daily_ai_message_limit_reached"


def test_monthly_usage_limit_is_enforced(build_client: Callable[..., TestClient]) -> None:
    with build_client(ai_daily_message_limit=5, ai_monthly_message_limit=1) as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Monthly limits"},
        ).json()
        first = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "No documents yet."},
        )
        second = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "Still no documents."},
        )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "monthly_ai_message_limit_reached"
