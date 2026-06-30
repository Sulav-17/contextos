from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from typing import Any, Final, cast
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
from contextos.domain.document_ingestion import extract_pdf_chunks, process_document
from contextos.infrastructure.database import DatabaseResource
from contextos.main import create_app

USER_A: Final = UUID("30000000-0000-4000-8000-000000000001")
USER_B: Final = UUID("30000000-0000-4000-8000-000000000002")
TEST_USERS: Final = (USER_A, USER_B)


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.fail(f"{name} is required for document API tests.")
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


async def clean_rows(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("SELECT set_config('app.actor_role', 'worker', true)"))
        await connection.execute(
            text("DELETE FROM documents WHERE user_id = ANY(:user_ids)"),
            {"user_ids": [str(user_id) for user_id in TEST_USERS]},
        )
        await connection.execute(text("SELECT set_config('app.actor_role', 'admin', true)"))
        await connection.execute(
            text("DELETE FROM users WHERE id = ANY(:user_ids)"),
            {"user_ids": [str(user_id) for user_id in TEST_USERS]},
        )


@pytest.fixture
async def clean_document_rows(migration_engine: AsyncEngine) -> AsyncGenerator[None]:
    await clean_rows(migration_engine)
    try:
        yield
    finally:
        await clean_rows(migration_engine)


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
            return Principal(USER_A, "documents-a@example.test", None)
        if authorization == "Bearer user-b":
            return Principal(USER_B, "documents-b@example.test", None)
        if authorization is None:
            raise AuthenticationError(AUTHENTICATION_REQUIRED.code)
        raise AuthenticationError(INVALID_AUTHENTICATION.code)


@pytest.fixture
def build_client(
    tmp_path: Path,
    clean_document_rows: None,
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., TestClient]:
    enqueued: list[UUID] = []

    def fake_enqueue(_settings: Settings, document_id: UUID) -> None:
        enqueued.append(document_id)

    monkeypatch.setattr("contextos.api.routes.documents.enqueue_document", fake_enqueue)

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
                "document_storage_root": tmp_path / "private-documents",
                **overrides,
            }
        )
        app = create_app(
            settings=settings,
            database_resource_factory=DatabaseResource,
            redis_resource_factory=FakeRedisResource,
            auth_provider_factory=lambda settings: FakeAuthProvider(),
        )
        app.state.enqueued_documents = enqueued
        return TestClient(app)

    return _build_client


def pdf_bytes(text_by_page: list[str]) -> bytes:
    page_refs = " ".join(f"{4 + index * 2} 0 R" for index in range(len(text_by_page)))
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{page_refs}] /Count {len(text_by_page)} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for index, text_value in enumerate(text_by_page):
        page_id = 4 + index * 2
        contents_id = page_id + 1
        escaped = text_value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode()
        page = (
            f"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 3 0 R >> >> "
            f"/MediaBox [0 0 612 792] /Contents {contents_id} 0 R >>"
        )
        objects.append(page.encode())
        objects.append(
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        )
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode())
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        (
            f"trailer\n<< /Root 1 0 R /Size {len(objects) + 1} >>\nstartxref\n{xref_start}\n%%EOF\n"
        ).encode()
    )
    return bytes(output)


def test_successful_pdf_upload_uses_private_opaque_storage_key(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client() as client:
        response = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={"file": ("notes.pdf", pdf_bytes(["Hello ContextOS."]), "application/pdf")},
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["original_filename"] == "notes.pdf"
    assert payload["status"] == "queued"
    assert payload["page_count"] == 1
    assert "storage_key" not in payload
    assert "private-documents" not in response.text
    assert len(payload["checksum_sha256"]) == 64


@pytest.mark.parametrize(
    ("filename", "content_type", "content", "expected_status"),
    [
        ("notes.txt", "application/pdf", b"%PDF-1.4\n", 422),
        ("notes.pdf", "text/plain", b"%PDF-1.4\n", 422),
        ("notes.pdf", "application/pdf", b"not a pdf", 422),
        ("notes.pdf", "application/pdf", b"", 422),
    ],
)
def test_upload_rejects_invalid_files(
    build_client: Callable[..., TestClient],
    filename: str,
    content_type: str,
    content: bytes,
    expected_status: int,
) -> None:
    with build_client() as client:
        response = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={"file": (filename, content, content_type)},
        )

    assert response.status_code == expected_status
    assert "private-documents" not in response.text


def test_upload_enforces_file_size_count_total_and_page_limits(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client(document_max_pdf_size_bytes=20) as client:
        oversized = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={"file": ("large.pdf", pdf_bytes(["large"]), "application/pdf")},
        )
    assert oversized.status_code == 413

    with build_client(document_max_per_user=1) as client:
        first = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={"file": ("one.pdf", pdf_bytes(["one"]), "application/pdf")},
        )
        second = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={"file": ("two.pdf", pdf_bytes(["two"]), "application/pdf")},
        )
    assert first.status_code == 201
    assert second.status_code == 409

    with build_client(document_max_total_size_bytes=400) as client:
        total = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-b"},
            files={"file": ("total.pdf", pdf_bytes(["total"]), "application/pdf")},
        )
    assert total.status_code == 409

    with build_client(document_max_pages=1) as client:
        pages = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-b"},
            files={"file": ("pages.pdf", pdf_bytes(["one", "two"]), "application/pdf")},
        )
    assert pages.status_code == 422


def test_tenant_safe_list_detail_download_retry_and_delete(
    build_client: Callable[..., TestClient],
) -> None:
    with build_client() as client:
        upload = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={"file": ("tenant.pdf", pdf_bytes(["Tenant A."]), "application/pdf")},
        )
        document_id = upload.json()["id"]
        list_a = client.get("/api/v1/documents", headers={"Authorization": "Bearer user-a"})
        detail_b = client.get(
            f"/api/v1/documents/{document_id}",
            headers={"Authorization": "Bearer user-b"},
        )
        download_b = client.get(
            f"/api/v1/documents/{document_id}/download",
            headers={"Authorization": "Bearer user-b"},
        )
        retry_b = client.post(
            f"/api/v1/documents/{document_id}/retry",
            headers={"Authorization": "Bearer user-b"},
        )
        delete_b = client.delete(
            f"/api/v1/documents/{document_id}",
            headers={"Authorization": "Bearer user-b"},
        )
        delete_a = client.delete(
            f"/api/v1/documents/{document_id}",
            headers={"Authorization": "Bearer user-a"},
        )
        list_after = client.get("/api/v1/documents", headers={"Authorization": "Bearer user-a"})

    assert list_a.status_code == 200
    assert [document["id"] for document in list_a.json()["documents"]] == [document_id]
    assert detail_b.status_code == 404
    assert download_b.status_code == 404
    assert retry_b.status_code == 404
    assert delete_b.status_code == 404
    assert delete_a.status_code == 204
    assert list_after.json()["documents"] == []


@pytest.mark.asyncio
async def test_successful_extraction_deterministic_chunks_and_retry_idempotency(
    build_client: Callable[..., TestClient],
    tmp_path: Path,
) -> None:
    with build_client(document_storage_root=tmp_path / "storage") as client:
        upload = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={
                "file": (
                    "extract.pdf",
                    pdf_bytes(["Alpha page.", "Beta page."]),
                    "application/pdf",
                )
            },
        )
        document_id = UUID(upload.json()["id"])
        settings = cast(Any, client.app).state.settings
        await process_document(document_id, settings)
        first = extract_pdf_chunks(
            pdf_bytes(["Alpha page.", "Beta page."]),
            max_pages=10,
            chunk_size=40,
            chunk_overlap=5,
        )
        second = extract_pdf_chunks(
            pdf_bytes(["Alpha page.", "Beta page."]),
            max_pages=10,
            chunk_size=40,
            chunk_overlap=5,
        )
        retry_ready = client.post(
            f"/api/v1/documents/{document_id}/retry",
            headers={"Authorization": "Bearer user-a"},
        )
        detail = client.get(
            f"/api/v1/documents/{document_id}",
            headers={"Authorization": "Bearer user-a"},
        )

    assert first == second
    assert [chunk[1] for chunk in first[2]] == [1, 2]
    assert retry_ready.status_code == 409
    assert detail.json()["status"] == "ready"
    assert detail.json()["extracted_character_count"] > 0


@pytest.mark.asyncio
async def test_no_extractable_text_failure_is_retryable(
    build_client: Callable[..., TestClient],
    tmp_path: Path,
) -> None:
    with build_client(document_storage_root=tmp_path / "storage") as client:
        upload = client.post(
            "/api/v1/documents",
            headers={"Authorization": "Bearer user-a"},
            files={"file": ("blank.pdf", pdf_bytes([""]), "application/pdf")},
        )
        document_id = UUID(upload.json()["id"])
        await process_document(document_id, cast(Any, client.app).state.settings)
        failed = client.get(
            f"/api/v1/documents/{document_id}",
            headers={"Authorization": "Bearer user-a"},
        )
        retry = client.post(
            f"/api/v1/documents/{document_id}/retry",
            headers={"Authorization": "Bearer user-a"},
        )

    assert failed.json()["status"] == "failed"
    assert failed.json()["failure_code"] == "no_extractable_text"
    assert retry.status_code == 200
    assert retry.json()["status"] == "queued"
