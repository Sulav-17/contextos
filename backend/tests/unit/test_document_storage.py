from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import UUID

import httpx
import pytest

from contextos.core.config import Settings
from contextos.infrastructure.document_storage import (
    LocalDocumentStorage,
    SupabaseDocumentStorage,
    SupabaseStorageError,
    build_document_storage,
)

USER_ID = UUID("30000000-0000-4000-8000-000000000001")


def test_local_document_storage_round_trip(
    make_settings: Callable[..., Settings],
    tmp_path: Path,
) -> None:
    settings = make_settings(document_storage_root=tmp_path / "documents")
    storage = LocalDocumentStorage(settings)

    stored = storage.write(b"%PDF-1.4\nhello", user_id=USER_ID)

    assert stored.storage_key.endswith(".pdf")
    assert storage.read_bytes(stored.storage_key) == b"%PDF-1.4\nhello"
    storage.delete(stored.storage_key)
    with pytest.raises(FileNotFoundError):
        storage.read_bytes(stored.storage_key)


def test_storage_factory_selects_supabase_backend(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        document_storage_backend="supabase",
        supabase_url="https://project.supabase.co",
        supabase_secret_key="server-secret",
        supabase_storage_bucket="contextos-private-documents",
    )

    assert isinstance(build_document_storage(settings), SupabaseDocumentStorage)


def test_supabase_document_storage_uses_private_tenant_scoped_paths(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, dict[str, str] | None, bytes | None, object]] = []

    def fake_post(
        url: str,
        *,
        content: bytes,
        headers: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        calls.append(("POST", url, headers, content, None))
        return httpx.Response(200, request=httpx.Request("POST", url))

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        calls.append(("GET", url, headers, None, None))
        return httpx.Response(200, content=b"%PDF-1.4\nstored", request=httpx.Request("GET", url))

    def fake_request(
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        json: object,
        timeout: float,
    ) -> httpx.Response:
        calls.append((method, url, headers, None, json))
        return httpx.Response(200, request=httpx.Request(method, url))

    monkeypatch.setattr("contextos.infrastructure.document_storage.httpx.post", fake_post)
    monkeypatch.setattr("contextos.infrastructure.document_storage.httpx.get", fake_get)
    monkeypatch.setattr("contextos.infrastructure.document_storage.httpx.request", fake_request)
    settings = make_settings(
        document_storage_backend="supabase",
        supabase_url="https://project.supabase.co",
        supabase_secret_key="server-secret",
        supabase_storage_bucket="contextos-private-documents",
        supabase_storage_path_prefix="documents",
    )
    storage = SupabaseDocumentStorage(settings)

    stored = storage.write(b"%PDF-1.4\nstored", user_id=USER_ID)
    content = storage.read_bytes(stored.storage_key)
    storage.delete(stored.storage_key)

    assert stored.storage_key.startswith(f"documents/users/{USER_ID}/documents/")
    assert stored.storage_key.endswith(".pdf")
    assert content == b"%PDF-1.4\nstored"
    assert "server-secret" not in stored.storage_key
    assert calls[0][0] == "POST"
    assert calls[0][2] == {
        "Authorization": "Bearer server-secret",
        "apikey": "server-secret",
        "Content-Type": "application/pdf",
        "x-upsert": "false",
    }
    assert calls[1][0] == "GET"
    assert calls[1][2] == {
        "Authorization": "Bearer server-secret",
        "apikey": "server-secret",
    }
    assert calls[2][0] == "DELETE"
    assert calls[2][2] == {
        "Authorization": "Bearer server-secret",
        "apikey": "server-secret",
        "Content-Type": "application/json",
    }
    assert calls[2][4] == {"prefixes": [stored.storage_key]}


def test_supabase_document_storage_wraps_http_errors_without_leaking_secrets(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(
        url: str,
        *,
        content: bytes,
        headers: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        response = httpx.Response(400, text="server-secret", request=httpx.Request("POST", url))
        response.raise_for_status()
        return response

    monkeypatch.setattr("contextos.infrastructure.document_storage.httpx.post", fake_post)
    settings = make_settings(
        document_storage_backend="supabase",
        supabase_url="https://project.supabase.co",
        supabase_secret_key="server-secret",
        supabase_storage_bucket="contextos-private-documents",
    )
    storage = SupabaseDocumentStorage(settings)

    with pytest.raises(SupabaseStorageError) as exc_info:
        storage.write(b"%PDF-1.4\nstored", user_id=USER_ID)

    assert "server-secret" not in str(exc_info.value)
    assert "private-documents" not in str(exc_info.value)
