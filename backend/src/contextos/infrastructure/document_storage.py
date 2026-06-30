from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from contextos.core.config import Settings


@dataclass(frozen=True, slots=True)
class StoredDocument:
    storage_key: str
    checksum_sha256: str
    size_bytes: int


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

    def write(self, content: bytes) -> StoredDocument:
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

    def delete(self, storage_key: str) -> None:
        path = self._resolve_key(storage_key)
        if path.exists() and not path.is_symlink():
            path.unlink()
