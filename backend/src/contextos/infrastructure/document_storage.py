from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import UUID, uuid4

import httpx

from contextos.core.config import Settings


@dataclass(frozen=True, slots=True)
class StoredDocument:
    storage_key: str
    checksum_sha256: str
    size_bytes: int


class SupabaseStorageError(RuntimeError):
    pass


class DocumentStorage(Protocol):
    def write(self, content: bytes, *, user_id: UUID) -> StoredDocument: ...
    def read_bytes(self, storage_key: str) -> bytes: ...
    def delete(self, storage_key: str) -> None: ...


class LocalDocumentStorage:
    def __init__(self, settings: Settings) -> None:
        self._root = settings.document_storage_root

    @property
    def root(self) -> Path:
        return self._root

    def _ensure_root(self) -> Path:
        self._root.mkdir(mode=0o700, parents=True, exist_ok=True)
        return self._root.resolve(strict=True)

    def _resolve_key(self, storage_key: str) -> Path:
        if "/" in storage_key or "\\" in storage_key or storage_key in {"", ".", ".."}:
            raise ValueError("invalid storage key")
        root = self._ensure_root()
        path = (root / storage_key).resolve(strict=False)
        if root != path and root not in path.parents:
            raise ValueError("storage key escaped root")
        return path

    def write(self, content: bytes, *, user_id: UUID) -> StoredDocument:
        root = self._ensure_root()
        storage_key = f"{uuid4()}.pdf"
        destination = self._resolve_key(storage_key)
        checksum = hashlib.sha256()
        fd, temp_name = tempfile.mkstemp(prefix=".upload-", suffix=".tmp", dir=root)
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as file:
                file.write(content)
                checksum.update(content)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temp_path, destination)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
        return StoredDocument(
            storage_key=storage_key,
            checksum_sha256=checksum.hexdigest(),
            size_bytes=len(content),
        )

    def read_path(self, storage_key: str) -> Path:
        path = self._resolve_key(storage_key)
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(storage_key)
        return path

    def read_bytes(self, storage_key: str) -> bytes:
        return self.read_path(storage_key).read_bytes()

    def delete(self, storage_key: str) -> None:
        path = self._resolve_key(storage_key)
        if path.exists() and not path.is_symlink():
            path.unlink()


class SupabaseDocumentStorage:
    def __init__(self, settings: Settings) -> None:
        if settings.supabase_secret_key is None:
            raise ValueError("Supabase storage requires a server secret key")
        if not settings.supabase_url or not settings.supabase_storage_bucket:
            raise ValueError("Supabase storage requires URL and bucket configuration")
        self._base_url = settings.supabase_url.rstrip("/")
        self._bucket = settings.supabase_storage_bucket
        self._path_prefix = settings.supabase_storage_path_prefix.strip("/")
        self._secret_key = settings.supabase_secret_key.get_secret_value()
        self._timeout = settings.readiness_timeout_seconds

    def write(self, content: bytes, *, user_id: UUID) -> StoredDocument:
        storage_key = self._storage_key(user_id)
        checksum = hashlib.sha256(content).hexdigest()
        try:
            response = httpx.post(
                self._object_url(storage_key),
                content=content,
                headers=self._supabase_auth_headers(
                    {
                        "Content-Type": "application/pdf",
                        "x-upsert": "false",
                    }
                ),
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SupabaseStorageError("Supabase storage request failed") from exc
        return StoredDocument(
            storage_key=storage_key,
            checksum_sha256=checksum,
            size_bytes=len(content),
        )

    def read_bytes(self, storage_key: str) -> bytes:
        self._validate_storage_key(storage_key)
        try:
            response = httpx.get(
                self._object_url(storage_key),
                headers=self._supabase_auth_headers(),
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise SupabaseStorageError("Supabase storage request failed") from exc
        if response.status_code == 404:
            raise FileNotFoundError(storage_key)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SupabaseStorageError("Supabase storage request failed") from exc
        return response.content

    def delete(self, storage_key: str) -> None:
        self._validate_storage_key(storage_key)
        try:
            response = httpx.request(
                "DELETE",
                f"{self._base_url}/storage/v1/object/{self._bucket}",
                headers=self._supabase_auth_headers({"Content-Type": "application/json"}),
                json={"prefixes": [storage_key]},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SupabaseStorageError("Supabase storage request failed") from exc

    def _storage_key(self, user_id: UUID) -> str:
        prefix = f"{self._path_prefix}/" if self._path_prefix else ""
        return f"{prefix}users/{user_id}/documents/{uuid4()}.pdf"

    def _object_url(self, storage_key: str) -> str:
        self._validate_storage_key(storage_key)
        return f"{self._base_url}/storage/v1/object/{self._bucket}/{storage_key}"

    def _validate_storage_key(self, storage_key: str) -> None:
        if storage_key in {"", ".", ".."} or "\\" in storage_key:
            raise ValueError("invalid storage key")
        parts = storage_key.split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise ValueError("invalid storage key")
        if not storage_key.endswith(".pdf"):
            raise ValueError("invalid storage key")

    def _supabase_auth_headers(self, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._secret_key}",
            "apikey": self._secret_key,
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers


def build_document_storage(settings: Settings) -> DocumentStorage:
    if settings.document_storage_backend == "local":
        return LocalDocumentStorage(settings)
    if settings.document_storage_backend == "supabase":
        return SupabaseDocumentStorage(settings)
    raise ValueError("unsupported document storage backend")
