from __future__ import annotations

import hashlib
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
from contextos.domain.ai import ProviderError, build_embedding_provider
from contextos.domain.chat import RetrievedChunk, retrieve_chunks, vector_literal
from contextos.infrastructure.database import DatabaseResource
from contextos.main import create_app
from tests.support import ensure_test_database, required_env, required_test_database_url

USER_A: Final = UUID("32000000-0000-4000-8000-000000000001")
USER_B: Final = UUID("32000000-0000-4000-8000-000000000002")
DOCUMENT_A: Final = UUID("33000000-0000-4000-8000-000000000001")
DOCUMENT_B: Final = UUID("33000000-0000-4000-8000-000000000002")
DOCUMENT_OTHER: Final = UUID("33000000-0000-4000-8000-000000000003")

def build_alembic_config() -> Config:
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[2] / "alembic"))
    config.set_main_option(
        "sqlalchemy.url",
        required_test_database_url(
            "CONTEXTOS_TEST_MIGRATION_DATABASE_URL",
            "CONTEXTOS_MIGRATION_DATABASE_URL",
        ),
    )
    return config


@pytest.fixture(scope="session")
def migrated_database() -> None:
    ensure_test_database()
    required_test_database_url("CONTEXTOS_TEST_DATABASE_URL", "CONTEXTOS_DATABASE_URL")
    required_test_database_url(
        "CONTEXTOS_TEST_MIGRATION_DATABASE_URL",
        "CONTEXTOS_MIGRATION_DATABASE_URL",
    )
    required_env("POSTGRES_APP_USER")
    command.upgrade(build_alembic_config(), "head")


@pytest.fixture
async def migration_engine(migrated_database: None) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        required_test_database_url(
            "CONTEXTOS_TEST_MIGRATION_DATABASE_URL",
            "CONTEXTOS_MIGRATION_DATABASE_URL",
        ),
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
                "database_url": required_test_database_url(
                    "CONTEXTOS_TEST_DATABASE_URL",
                    "CONTEXTOS_DATABASE_URL",
                ),
                "migration_database_url": required_test_database_url(
                    "CONTEXTOS_TEST_MIGRATION_DATABASE_URL",
                    "CONTEXTOS_MIGRATION_DATABASE_URL",
                ),
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
    create_chunk: bool = True,
) -> None:
    provider = build_embedding_provider(settings)
    vector = embedding or (await provider.embed([content or filename]))[0]
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
        if create_chunk:
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


async def mark_document_deleted(engine: AsyncEngine, *, user_id: UUID, document_id: UUID) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'worker', true)"))
        await connection.execute(
            text(
                """
                UPDATE documents
                SET status = 'deleted', deleted_at = now()
                WHERE user_id = :user_id AND id = :document_id
                """
            ),
            {"user_id": str(user_id), "document_id": str(document_id)},
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
async def test_conversations_are_tenant_isolated_and_general_without_selected_documents(
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
        general = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What is not in the files?"},
        )

    assert cross_tenant.status_code == 404
    assert general.status_code == 200
    assert general.json()["source_mode"] == "general"
    assert general.json()["message"]["citations"] == []
    assert general.json()["message"]["memory_references"] == []
    assert general.json()["message"]["content"].startswith("General answer:")


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


@pytest.mark.asyncio
async def test_selected_document_broad_summary_bypasses_threshold_with_citations(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client(retrieval_similarity_threshold=1.0) as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="selected.pdf",
            content="Selected report explains renewal dates, payment duties, and notice windows.",
            embedding=fixed_vector(0.0, 1.0),
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Summary"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={
                "question": "What is the document about?",
                "document_ids": [str(DOCUMENT_A)],
            },
        )

    assert answer.status_code == 200
    payload = answer.json()
    assert payload["evidence_status"] == "grounded"
    assert payload["message"]["citations"][0]["document_id"] == str(DOCUMENT_A)
    assert "selected.pdf" in payload["message"]["content"]


@pytest.mark.asyncio
async def test_selected_document_summary_excludes_unselected_documents(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client(retrieval_similarity_threshold=1.0) as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="selected.pdf",
            content="Selected document is about contract renewal terms.",
            embedding=fixed_vector(0.0, 1.0),
        )
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_B,
            filename="unselected.pdf",
            content="Unselected document contains medical appointment details.",
            embedding=fixed_vector(0.0, 1.0),
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Selected only"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={
                "question": "Summarize this document.",
                "document_ids": [str(DOCUMENT_A)],
            },
        )

    payload = answer.json()
    assert answer.status_code == 200
    assert {citation["document_id"] for citation in payload["message"]["citations"]} == {
        str(DOCUMENT_A)
    }
    assert "unselected.pdf" not in payload["message"]["content"]
    assert "medical appointment" not in payload["message"]["content"]


@pytest.mark.asyncio
async def test_normal_selected_factual_query_still_uses_similarity_threshold(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client(retrieval_similarity_threshold=1.0) as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="threshold-selected.pdf",
            content="This document describes ordinary lease renewal terms.",
            embedding=fixed_vector(0.0, 1.0),
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Threshold selected"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "Who signed the agreement?", "document_ids": [str(DOCUMENT_A)]},
    )

    assert answer.status_code == 200
    assert answer.json()["source_mode"] == "insufficient_evidence"
    assert answer.json()["message"]["citations"] == []


@pytest.mark.asyncio
async def test_broad_question_without_selected_documents_does_not_bypass_threshold(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client(retrieval_similarity_threshold=1.0) as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="not-selected.pdf",
            content="This document has enough text for a summary if selected.",
            embedding=fixed_vector(0.0, 1.0),
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "No selected docs"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What is the document about?"},
        )

    assert answer.status_code == 200
    assert answer.json()["source_mode"] == "general"
    assert answer.json()["message"]["citations"] == []


@pytest.mark.asyncio
async def test_selected_scope_persists_and_is_removed_when_document_unavailable(
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
            filename="scope-a.pdf",
            content="Scope A document has grounded evidence.",
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Scope"},
        ).json()
        empty_detail = client.get(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
        )
        client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What is this document about?", "document_ids": [str(DOCUMENT_A)]},
        )
        detail = client.get(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
        )
        await mark_document_deleted(migration_engine, user_id=USER_A, document_id=DOCUMENT_A)
        after_delete = client.get(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
        )

    assert empty_detail.status_code == 200
    assert empty_detail.json()["selected_document_ids"] == []
    assert detail.json()["selected_document_ids"] == [str(DOCUMENT_A)]
    assert after_delete.json()["selected_document_ids"] == []


@pytest.mark.asyncio
async def test_different_conversations_retain_different_document_scopes(
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
            filename="scope-a.pdf",
            content="Scope A document has renewal evidence.",
        )
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_B,
            filename="scope-b.pdf",
            content="Scope B document has policy evidence.",
        )
        first = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "First"},
        ).json()
        second = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Second"},
        ).json()
        client.post(
            f"/api/v1/conversations/{first['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What is this document about?", "document_ids": [str(DOCUMENT_A)]},
        )
        client.post(
            f"/api/v1/conversations/{second['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What is this document about?", "document_ids": [str(DOCUMENT_B)]},
        )
        first_detail = client.get(
            f"/api/v1/conversations/{first['id']}",
            headers={"Authorization": "Bearer user-a"},
        )
        second_detail = client.get(
            f"/api/v1/conversations/{second['id']}",
            headers={"Authorization": "Bearer user-a"},
        )

    assert first_detail.json()["selected_document_ids"] == [str(DOCUMENT_A)]
    assert second_detail.json()["selected_document_ids"] == [str(DOCUMENT_B)]


@pytest.mark.asyncio
async def test_cross_user_selected_document_id_is_blocked(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client() as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_B,
            document_id=DOCUMENT_OTHER,
            filename="other-user.pdf",
            content="Other user's document must not be scoped.",
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Cross user"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={
                "question": "What is this document about?",
                "document_ids": [str(DOCUMENT_OTHER)],
            },
        )
        detail = client.get(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
        )

    assert answer.status_code == 404
    assert answer.json()["error"]["code"] == "document_not_found"
    assert detail.json()["selected_document_ids"] == []


@pytest.mark.asyncio
async def test_selected_document_without_text_returns_safe_fallback(
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
            filename="empty.pdf",
            content="",
            create_chunk=False,
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Empty"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What is the document about?", "document_ids": [str(DOCUMENT_A)]},
        )

    assert answer.status_code == 200
    assert answer.json()["evidence_status"] == "insufficient_evidence"
    assert answer.json()["message"]["citations"] == []


@pytest.mark.asyncio
async def test_provider_failure_does_not_create_messages_or_increment_usage(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingChatProvider:
        provider = "test-failure"
        model = "test-failure-model"

        async def generate(self, request: object) -> object:
            del request
            raise ProviderError()

    monkeypatch.setattr(
        "contextos.domain.chat.build_chat_provider",
        lambda settings: FailingChatProvider(),
    )

    with build_client() as client:
        settings = cast(Any, client.app).state.settings

        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="provider-failure.pdf",
            content="Provider failure should not duplicate accepted messages.",
        )

        conversation_response = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Provider failure"},
        )
        assert conversation_response.status_code == 201
        conversation = conversation_response.json()

        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={
                "question": "What is this document about?",
                "document_ids": [str(DOCUMENT_A)],
            },
        )

        detail = client.get(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
        )

        usage = client.get(
            "/api/v1/usage",
            headers={"Authorization": "Bearer user-a"},
        )

    assert answer.status_code == 503

    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["messages"] == []

    assert usage.status_code == 200
    usage_payload = usage.json()
    assert usage_payload["daily"]["used"] == 0
    assert usage_payload["monthly"]["used"] == 0


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


def test_first_message_applies_deterministic_title(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "New conversation"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "   What does ContextOS know?\n\nPlease cite it.   "},
        )
        detail = client.get(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
        )

    assert answer.status_code == 200
    assert detail.json()["title"] == "What does ContextOS know? Please cite it."


def test_first_message_title_truncates_and_manual_title_is_not_overwritten(
    build_client: Callable[..., TestClient],
) -> None:
    long_question = (
        "How should I compare the document evidence about private retrieval "
        "against the cited answer?"
    )
    with build_client() as client:
        untitled = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "New conversation"},
        ).json()
        manual = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Manual research"},
        ).json()
        client.post(
            f"/api/v1/conversations/{untitled['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": long_question},
        )
        client.post(
            f"/api/v1/conversations/{manual['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "Should not replace this title."},
        )
        untitled_detail = client.get(
            f"/api/v1/conversations/{untitled['id']}",
            headers={"Authorization": "Bearer user-a"},
        ).json()
        manual_detail = client.get(
            f"/api/v1/conversations/{manual['id']}",
            headers={"Authorization": "Bearer user-a"},
        ).json()

    assert untitled_detail["title"] == "How should I compare the document evidence about private..."
    assert len(untitled_detail["title"]) <= 60
    assert manual_detail["title"] == "Manual research"


def test_conversation_rename_validates_and_is_tenant_isolated(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Original"},
        ).json()
        unauthenticated = client.patch(
            f"/api/v1/conversations/{conversation['id']}",
            json={"title": "No session"},
        )
        blank = client.patch(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "   \n  "},
        )
        too_long = client.patch(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "x" * 121},
        )
        cross_tenant = client.patch(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-b"},
            json={"title": "Other user"},
        )
        renamed = client.patch(
            f"/api/v1/conversations/{conversation['id']}",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "  Updated   title  "},
        )

    assert unauthenticated.status_code == 401
    assert blank.status_code == 422
    assert too_long.status_code == 422
    assert cross_tenant.status_code == 404
    assert renamed.status_code == 200
    assert renamed.json()["title"] == "Updated title"
    assert renamed.json()["updated_at"] != conversation["updated_at"]


def test_conversation_archive_unarchive_updates_default_history(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Archive me"},
        ).json()
        archived = client.post(
            f"/api/v1/conversations/{conversation['id']}/archive",
            headers={"Authorization": "Bearer user-a"},
        )
        active_list = client.get(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
        )
        archive_list = client.get(
            "/api/v1/conversations?archived=true",
            headers={"Authorization": "Bearer user-a"},
        )
        restored = client.post(
            f"/api/v1/conversations/{conversation['id']}/unarchive",
            headers={"Authorization": "Bearer user-a"},
        )

    assert archived.status_code == 200
    assert archived.json()["archived_at"] is not None
    assert active_list.json()["conversations"] == []
    assert archive_list.json()["conversations"][0]["id"] == conversation["id"]
    assert restored.status_code == 200
    assert restored.json()["archived_at"] is None


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


def test_memory_manual_lifecycle_is_authenticated_and_tenant_scoped(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client(memory_retrieval_similarity_threshold=0.1) as client:
        unauthenticated = client.post(
            "/api/v1/memories",
            json={"memory_type": "preference", "content": "renewal preference concise"},
        )
        created = client.post(
            "/api/v1/memories",
            headers={"Authorization": "Bearer user-a"},
            json={"memory_type": "preference", "content": "renewal preference concise"},
        )
        memory_id = created.json()["id"]
        cross_tenant = client.post(
            f"/api/v1/memories/{memory_id}/disable",
            headers={"Authorization": "Bearer user-b"},
        )
        disabled = client.post(
            f"/api/v1/memories/{memory_id}/disable",
            headers={"Authorization": "Bearer user-a"},
        )
        enabled = client.post(
            f"/api/v1/memories/{memory_id}/enable",
            headers={"Authorization": "Bearer user-a"},
        )
        deleted = client.delete(
            f"/api/v1/memories/{memory_id}",
            headers={"Authorization": "Bearer user-a"},
        )

    assert unauthenticated.status_code == 401
    assert created.status_code == 201
    assert created.json()["status"] == "approved"
    assert cross_tenant.status_code == 404
    assert disabled.status_code == 200
    assert disabled.json()["status"] == "disabled"
    assert enabled.status_code == 200
    assert enabled.json()["status"] == "approved"
    assert deleted.status_code == 204


def test_memory_suggestions_require_user_authored_explicit_intent(
    build_client: Callable[..., TestClient],
) -> None:
    statement = (
        "Remember that my preferred deployment target is a browser-installable PWA "
        "before any native app."
    )
    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Memory suggestions"},
        ).json()
        suggested = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": statement},
        )
        secret = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "Remember that my password is swordfish."},
        )
        suggestions = client.get(
            "/api/v1/memories/suggestions",
            headers={"Authorization": "Bearer user-a"},
        )
        memory = suggestions.json()["memories"][0]
        approved = client.post(
            f"/api/v1/memories/{memory['id']}/approve",
            headers={"Authorization": "Bearer user-a"},
        )

    assert suggested.status_code == 200
    assert suggested.json()["source_mode"] == "memory_suggestion_created"
    assert suggested.json()["message"]["content"] == (
        "Memory suggestion created. Awaiting approval before it can influence answers."
    )
    assert suggested.json()["message"]["citations"] == []
    assert suggested.json()["usage"]["daily"]["used"] == 0
    assert secret.status_code == 200
    assert len(suggestions.json()["memories"]) == 1
    assert suggestions.json()["memories"][0]["status"] == "suggested"
    assert suggestions.json()["memories"][0]["memory_type"] == "preference"
    assert suggestions.json()["memories"][0]["source_conversation_id"] == conversation["id"]
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"


@pytest.mark.parametrize(
    ("prompt", "memory_type"),
    [
        ("Save this deployment target is browser install first.", "other"),
        ("I prefer concise renewal summaries.", "preference"),
        ("My goal is launch the private beta this month.", "goal"),
        ("I decided to avoid native wrappers for now.", "decision"),
        ("From now on keep answers under five bullets.", "preference"),
    ],
)
def test_explicit_memory_save_commands_still_create_suggestions(
    build_client: Callable[..., TestClient],
    prompt: str,
    memory_type: str,
) -> None:
    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Explicit saves"},
        ).json()
        response = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": prompt},
        )
        suggestions = client.get(
            "/api/v1/memories/suggestions",
            headers={"Authorization": "Bearer user-a"},
        )

    assert response.status_code == 200
    assert response.json()["source_mode"] == "memory_suggestion_created"
    assert suggestions.json()["memories"][0]["memory_type"] == memory_type


def test_duplicate_valid_save_statement_does_not_create_duplicates(
    build_client: Callable[..., TestClient],
) -> None:
    prompt = "Remember that I prefer dark mode."
    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Duplicate saves"},
        ).json()
        first = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": prompt},
        )
        second = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": prompt},
        )
        suggestions = client.get(
            "/api/v1/memories/suggestions",
            headers={"Authorization": "Bearer user-a"},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["source_mode"] == "memory_suggestion_created"
    assert second.json()["source_mode"] == "memory_suggestion_created"
    assert len(suggestions.json()["memories"]) == 1


def test_memory_question_forms_do_not_create_suggestions(
    build_client: Callable[..., TestClient],
) -> None:
    questions = [
        "What is my goal?",
        "What did I decide?",
        "Do you remember what I prefer?",
    ]
    with build_client(memory_retrieval_similarity_threshold=0.1) as client:
        client.post(
            "/api/v1/memories",
            headers={"Authorization": "Bearer user-a"},
            json={"memory_type": "preference", "content": "deployment target browser install"},
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Memory questions"},
        ).json()
        responses = [
            client.post(
                f"/api/v1/conversations/{conversation['id']}/messages",
                headers={"Authorization": "Bearer user-a"},
                json={"question": question},
            )
            for question in questions
        ]
        suggestions = client.get(
            "/api/v1/memories/suggestions",
            headers={"Authorization": "Bearer user-a"},
        )

    assert suggestions.json()["memories"] == []
    for response in responses:
        assert response.status_code == 200


def test_memory_aware_question_uses_approved_memory_without_creating_suggestion(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client(memory_retrieval_similarity_threshold=0.1) as client:
        client.post(
            "/api/v1/memories",
            headers={"Authorization": "Bearer user-a"},
            json={
                "memory_type": "preference",
                "content": (
                    "my preferred deployment target is a browser-installable PWA before any "
                    "native app."
                ),
            },
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Memory retrieval"},
        ).json()
        response = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "What deployment target do I prefer?"},
        )
        suggestions = client.get(
            "/api/v1/memories/suggestions",
            headers={"Authorization": "Bearer user-a"},
        )

    assert response.status_code == 200
    assert response.json()["source_mode"] == "memory"
    assert response.json()["message"]["citations"] == []
    assert response.json()["message"]["content"] == (
        "Your preferred deployment target is a browser-installable PWA before any native app."
    )
    assert response.json()["message"]["memory_references"][0]["content"] == (
        "my preferred deployment target is a browser-installable PWA before any native app."
    )
    assert suggestions.json()["memories"] == []


def test_approved_memory_is_returned_separately_from_document_citations(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client(memory_retrieval_similarity_threshold=0.1) as client:
        created = client.post(
            "/api/v1/memories",
            headers={"Authorization": "Bearer user-a"},
            json={"memory_type": "preference", "content": "renewal preference concise"},
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Memory answer"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "renewal"},
        )
        client.post(
            f"/api/v1/memories/{created.json()['id']}/disable",
            headers={"Authorization": "Bearer user-a"},
        )
        after_disable = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "renewal"},
        )

    assert answer.status_code == 200
    assert answer.json()["memory_used"] is True
    assert answer.json()["source_mode"] == "memory"
    assert answer.json()["message"]["citations"] == []
    assert answer.json()["message"]["memory_references"][0]["content"] == (
        "renewal preference concise"
    )
    assert "Remembered information" in answer.json()["message"]["content"]
    assert after_disable.status_code == 200
    assert after_disable.json()["memory_used"] is False
    assert after_disable.json()["source_mode"] == "general"
    assert after_disable.json()["message"]["memory_references"] == []


@pytest.mark.parametrize(
    "prompt",
    [
        "?",
        "!!!",
        "Save this ?",
        "Remember that",
        "Remember that ?",
        "Save this",
        "Remember that ???",
    ],
)
def test_malformed_memory_suggestion_content_is_rejected(
    build_client: Callable[..., TestClient],
    prompt: str,
) -> None:
    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Malformed saves"},
        ).json()
        response = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": prompt},
        )
        suggestions = client.get(
            "/api/v1/memories/suggestions",
            headers={"Authorization": "Bearer user-a"},
        )

    assert response.status_code == 200
    assert suggestions.json()["memories"] == []


@pytest.mark.parametrize(
    "prompt",
    [
        "?",
        "!!!",
        "Remember that",
    ],
)
def test_punctuation_only_or_bare_content_is_rejected(
    build_client: Callable[..., TestClient],
    prompt: str,
) -> None:
    with build_client() as client:
        response = client.post(
            "/api/v1/memories",
            headers={"Authorization": "Bearer user-a"},
            json={"memory_type": "other", "content": prompt},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("content", ["?", "Remember that"])
async def test_malformed_suggestion_cannot_be_approved(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
    content: str,
) -> None:
    with build_client() as client:
        memory_id = UUID("71000000-0000-4000-8000-000000000001")
        conversation_id = UUID("72000000-0000-4000-8000-000000000001")
        message_id = UUID("73000000-0000-4000-8000-000000000001")
        async with migration_engine.begin() as connection:
            await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
            await connection.execute(
                text(
                    """
                    INSERT INTO users (id, email, role, status)
                    VALUES (:user_id, :email, 'user', 'active')
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {"user_id": str(USER_A), "email": "user-a@example.test"},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO conversations (id, user_id, title)
                    VALUES (:conversation_id, :user_id, 'Invalid memory source')
                    """
                ),
                {"conversation_id": str(conversation_id), "user_id": str(USER_A)},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO messages (
                      id, conversation_id, user_id, role, content, status
                    )
                    VALUES (
                      :message_id, :conversation_id, :user_id, 'user', 'seed', 'completed'
                    )
                    """
                ),
                {
                    "message_id": str(message_id),
                    "conversation_id": str(conversation_id),
                    "user_id": str(USER_A),
                },
            )
            await connection.execute(
                    text(
                        """
                        INSERT INTO memories (
                          id, user_id, memory_type, content, status, source_kind,
                          source_conversation_id, source_message_id, content_sha256
                        )
                        VALUES (
                          :memory_id, :user_id, 'preference', :content, 'suggested',
                          'conversation', :conversation_id, :message_id, repeat('a', 64)
                        )
                        """
                    ),
                        {
                            "memory_id": str(memory_id),
                            "user_id": str(USER_A),
                            "conversation_id": str(conversation_id),
                            "message_id": str(message_id),
                            "content": content,
                        },
                    )
        approval = client.post(
            f"/api/v1/memories/{memory_id}/approve",
            headers={"Authorization": "Bearer user-a"},
        )

    assert approval.status_code == 404


@pytest.mark.asyncio
async def test_documents_and_memory_response_keeps_sources_separate(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
) -> None:
    with build_client(memory_retrieval_similarity_threshold=0.1) as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="deployment.pdf",
            content="Deployment docs say browser install is supported with a service worker.",
        )
        client.post(
            "/api/v1/memories",
            headers={"Authorization": "Bearer user-a"},
            json={"memory_type": "preference", "content": "deployment target browser install"},
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Combined"},
        ).json()
        answer = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "deployment browser install", "document_ids": [str(DOCUMENT_A)]},
        )

    payload = answer.json()
    assert answer.status_code == 200
    assert payload["source_mode"] == "documents_and_memory"
    assert payload["message"]["citations"][0]["document_id"] == str(DOCUMENT_A)
    assert payload["message"]["memory_references"][0]["content"] == (
        "deployment target browser install"
    )


@pytest.mark.asyncio
async def test_dashboard_returns_tenant_scoped_counts_and_recent_items(
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
            filename="alpha.pdf",
            content="Alpha content",
        )
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_B,
            filename="beta.pdf",
            content="Beta content",
        )
        await mark_document_deleted(migration_engine, user_id=USER_A, document_id=DOCUMENT_B)
        client.post(
            "/api/v1/memories",
            headers={"Authorization": "Bearer user-a"},
            json={"memory_type": "preference", "content": "alpha preference"},
        )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Dashboard conversation"},
        ).json()
        client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": "Remember that I prefer concise answers."},
        )
        client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-b"},
            json={"title": "Other tenant"},
        )

        response = client.get("/api/v1/dashboard", headers={"Authorization": "Bearer user-a"})

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "private, no-store"
    payload = response.json()
    assert payload["counts"] == {
        "active_documents": 1,
        "active_conversations": 1,
        "approved_memories": 1,
        "pending_suggestions": 1,
    }
    assert payload["recent_documents"][0]["original_filename"] == "alpha.pdf"
    assert len(payload["recent_documents"]) == 1
    assert payload["recent_conversations"][0]["title"] == "Dashboard conversation"
    assert payload["recent_memories"][0]["content"] == "alpha preference"
    assert payload["pending_suggestions"][0]["status"] == "suggested"


@pytest.mark.parametrize(
    ("question", "expected_prefix"),
    [
        ("How many documents do I have?", "You have 1 document."),
        ("What files are in my library?", "Your library contains: alpha.pdf."),
        ("How many conversations do I have?", "You have 1 conversation."),
        (
            "How many approved, suggested, or disabled memories do I have?",
            "You have 1 approved, 1 suggested, and 0 disabled memories.",
        ),
        ("What is my usage today?", "Today you have used 0 of 20. 20 remaining."),
        ("What is my monthly usage?", "This month you have used 0 of 200. 200 remaining."),
    ],
)
@pytest.mark.asyncio
async def test_workspace_state_intents_are_contextos_only_and_skip_provider_calls(
    build_client: Callable[..., TestClient],
    migration_engine: AsyncEngine,
    question: str,
    expected_prefix: str,
) -> None:
    with build_client(llm_provider="gemini", embedding_provider="fake") as client:
        settings = cast(Any, client.app).state.settings
        await seed_document(
            migration_engine,
            settings=settings,
            user_id=USER_A,
            document_id=DOCUMENT_A,
            filename="alpha.pdf",
            content="Alpha content",
        )
        async with migration_engine.begin() as connection:
            await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
            await connection.execute(
                text(
                    """
                    INSERT INTO memories (
                      user_id, memory_type, content, status, source_kind, content_sha256
                    )
                    VALUES
                      (
                        :user_id, 'preference', 'alpha preference',
                        'approved', 'manual', repeat('a', 64)
                      ),
                      (
                        :user_id, 'preference', 'needs review',
                        'suggested', 'manual', repeat('b', 64)
                      )
                    """
                ),
                {"user_id": str(USER_A)},
            )
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "Workspace state"},
        ).json()
        response = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": question},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_mode"] == "contextos"
    assert payload["message"]["source_mode"] == "contextos"
    assert payload["message"]["content"] == expected_prefix
    assert payload["message"]["citations"] == []
    assert payload["message"]["memory_references"] == []


def test_general_chat_without_context_skips_embedding_and_logs_safe_timings(
    build_client: Callable[..., TestClient],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_embedding_provider(_settings: Settings) -> object:
        raise AssertionError("embedding provider should not be built")

    timing_logs: list[tuple[object, ...]] = []

    def capture_timing_log(message: str, *args: object) -> None:
        timing_logs.append((message, *args))

    monkeypatch.setattr("contextos.domain.chat.build_embedding_provider", fail_embedding_provider)
    monkeypatch.setattr("contextos.domain.chat.logger.info", capture_timing_log)
    private_prompt = "Explain latency without using secret-token-123 or private-memory-content."

    with build_client() as client:
        conversation = client.post(
            "/api/v1/conversations",
            headers={"Authorization": "Bearer user-a"},
            json={"title": "General"},
        ).json()
        response = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers={"Authorization": "Bearer user-a"},
            json={"question": private_prompt},
        )

    assert response.status_code == 200
    assert response.json()["source_mode"] == "general"
    stages = [str(args[1]) for args in timing_logs]
    serialized_logs = repr(timing_logs)
    assert "embedding_skipped" in stages
    assert "gemini_generation" in stages
    assert all(
        args[0] == "conversation_message_stage stage=%s duration_ms=%.2f total_ms=%.2f"
        for args in timing_logs
    )
    assert "secret-token-123" not in serialized_logs
    assert "private-memory-content" not in serialized_logs
    assert str(conversation["id"]) not in serialized_logs
