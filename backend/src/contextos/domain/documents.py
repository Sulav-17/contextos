from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Literal, cast
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.engine import CursorResult, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

DocumentStatus = Literal["uploaded", "queued", "processing", "ready", "failed", "deleted"]


class DocumentResponse(BaseModel):
    id: UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str | None
    status: DocumentStatus
    page_count: int | None
    extracted_character_count: int | None
    failure_code: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class DocumentRecord(DocumentResponse):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    storage_key: str
    deleted_at: datetime | None


def sanitize_filename(filename: str) -> str:
    name = filename.replace("\\", "/").split("/")[-1].strip()
    name = re.sub(r"[\x00-\x1f\x7f]+", "", name)
    name = re.sub(r"\s+", " ", name)
    return name[:240] or "document.pdf"


def document_response_from_row(row: RowMapping) -> DocumentResponse:
    record = DocumentRecord.model_validate(dict(row))
    return DocumentResponse.model_validate(record.model_dump())


def document_record_from_row(row: RowMapping) -> DocumentRecord:
    return DocumentRecord.model_validate(dict(row))


async def count_active_documents(session: AsyncSession, user_id: UUID) -> int:
    result = await session.execute(
        text(
            """
            SELECT count(*)
            FROM documents
            WHERE user_id = :user_id AND deleted_at IS NULL
            """
        ),
        {"user_id": str(user_id)},
    )
    return int(result.scalar_one())


async def total_active_document_size(session: AsyncSession, user_id: UUID) -> int:
    result = await session.execute(
        text(
            """
            SELECT COALESCE(sum(size_bytes), 0)
            FROM documents
            WHERE user_id = :user_id AND deleted_at IS NULL
            """
        ),
        {"user_id": str(user_id)},
    )
    return int(result.scalar_one())


async def create_queued_document(
    session: AsyncSession,
    *,
    user_id: UUID,
    original_filename: str,
    storage_key: str,
    mime_type: str,
    size_bytes: int,
    checksum_sha256: str,
    page_count: int,
) -> DocumentResponse:
    now = datetime.now(UTC)
    result = await session.execute(
        text(
            """
            INSERT INTO documents (
              user_id,
              original_filename,
              storage_key,
              mime_type,
              size_bytes,
              checksum_sha256,
              status,
              page_count,
              created_at,
              updated_at
            )
            VALUES (
              :user_id,
              :original_filename,
              :storage_key,
              :mime_type,
              :size_bytes,
              :checksum_sha256,
              'queued',
              :page_count,
              :now,
              :now
            )
            RETURNING id, user_id, original_filename, storage_key, mime_type, size_bytes,
              checksum_sha256, status, page_count, extracted_character_count,
              failure_code, failure_reason, created_at, updated_at, processed_at, deleted_at
            """
        ),
        {
            "user_id": str(user_id),
            "original_filename": original_filename,
            "storage_key": storage_key,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "checksum_sha256": checksum_sha256,
            "page_count": page_count,
            "now": now,
        },
    )
    return document_response_from_row(result.mappings().one())


async def list_documents(session: AsyncSession, user_id: UUID) -> DocumentListResponse:
    result = await session.execute(
        text(
            """
            SELECT id, user_id, original_filename, storage_key, mime_type, size_bytes,
              checksum_sha256, status, page_count, extracted_character_count,
              failure_code, failure_reason, created_at, updated_at, processed_at, deleted_at
            FROM documents
            WHERE user_id = :user_id AND deleted_at IS NULL
            ORDER BY created_at DESC, id DESC
            """
        ),
        {"user_id": str(user_id)},
    )
    return DocumentListResponse(
        documents=[document_response_from_row(row) for row in result.mappings().all()]
    )


async def get_document(
    session: AsyncSession,
    *,
    user_id: UUID,
    document_id: UUID,
) -> DocumentRecord | None:
    result = await session.execute(
        text(
            """
            SELECT id, user_id, original_filename, storage_key, mime_type, size_bytes,
              checksum_sha256, status, page_count, extracted_character_count,
              failure_code, failure_reason, created_at, updated_at, processed_at, deleted_at
            FROM documents
            WHERE id = :document_id AND user_id = :user_id AND deleted_at IS NULL
            """
        ),
        {"document_id": str(document_id), "user_id": str(user_id)},
    )
    row = result.mappings().one_or_none()
    return document_record_from_row(row) if row is not None else None


async def get_document_for_worker(
    session: AsyncSession, document_id: UUID
) -> DocumentRecord | None:
    result = await session.execute(
        text(
            """
            SELECT id, user_id, original_filename, storage_key, mime_type, size_bytes,
              checksum_sha256, status, page_count, extracted_character_count,
              failure_code, failure_reason, created_at, updated_at, processed_at, deleted_at
            FROM documents
            WHERE id = :document_id AND deleted_at IS NULL
            """
        ),
        {"document_id": str(document_id)},
    )
    row = result.mappings().one_or_none()
    return document_record_from_row(row) if row is not None else None


async def mark_processing(session: AsyncSession, document_id: UUID) -> bool:
    result = await session.execute(
        text(
            """
            UPDATE documents
            SET status = 'processing',
                processing_started_at = :now,
                updated_at = :now,
                failure_code = NULL,
                failure_reason = NULL
            WHERE id = :document_id
              AND deleted_at IS NULL
              AND status IN ('queued', 'failed')
            """
        ),
        {"document_id": str(document_id), "now": datetime.now(UTC)},
    )
    return cast(CursorResult[object], result).rowcount == 1


async def replace_chunks(
    session: AsyncSession,
    *,
    document_id: UUID,
    user_id: UUID,
    chunks: list[tuple[int, int, str]],
    page_count: int,
    extracted_character_count: int,
) -> None:
    now = datetime.now(UTC)
    await session.execute(
        text("DELETE FROM document_chunks WHERE document_id = :document_id"),
        {"document_id": str(document_id)},
    )
    for chunk_index, page_number, content in chunks:
        await session.execute(
            text(
                """
                INSERT INTO document_chunks (
                  document_id, user_id, chunk_index, page_number, content,
                  character_count, content_sha256, created_at
                )
                VALUES (
                  :document_id, :user_id, :chunk_index, :page_number, :content,
                  :character_count, :content_sha256, :now
                )
                """
            ),
            {
                "document_id": str(document_id),
                "user_id": str(user_id),
                "chunk_index": chunk_index,
                "page_number": page_number,
                "content": content,
                "character_count": len(content),
                "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "now": now,
            },
        )
    await session.execute(
        text(
            """
            UPDATE documents
            SET status = 'processing',
                page_count = :page_count,
                extracted_character_count = :extracted_character_count,
                failure_code = NULL,
                failure_reason = NULL,
                processed_at = :now,
                updated_at = :now
            WHERE id = :document_id AND deleted_at IS NULL
            """
        ),
        {
            "document_id": str(document_id),
            "page_count": page_count,
            "extracted_character_count": extracted_character_count,
            "now": now,
        },
    )


async def list_chunks_needing_embeddings(
    session: AsyncSession,
    *,
    document_id: UUID,
    embedding_provider: str,
    embedding_model: str,
    embedding_dimension: int,
) -> list[tuple[UUID, str]]:
    result = await session.execute(
        text(
            """
            SELECT id, content
            FROM document_chunks
            WHERE document_id = :document_id
              AND (
                embedding IS NULL
                OR embedding_provider IS DISTINCT FROM :embedding_provider
                OR embedding_model IS DISTINCT FROM :embedding_model
                OR embedding_dimension IS DISTINCT FROM :embedding_dimension
              )
            ORDER BY chunk_index
            """
        ),
        {
            "document_id": str(document_id),
            "embedding_provider": embedding_provider,
            "embedding_model": embedding_model,
            "embedding_dimension": embedding_dimension,
        },
    )
    return [(row["id"], row["content"]) for row in result.mappings()]


def embedding_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


async def store_chunk_embeddings(
    session: AsyncSession,
    *,
    embeddings: list[tuple[UUID, list[float]]],
    embedding_provider: str,
    embedding_model: str,
    embedding_dimension: int,
) -> None:
    now = datetime.now(UTC)
    for chunk_id, embedding in embeddings:
        await session.execute(
            text(
                """
                UPDATE document_chunks
                SET embedding = CAST(:embedding AS vector),
                    embedding_provider = :embedding_provider,
                    embedding_model = :embedding_model,
                    embedding_dimension = :embedding_dimension,
                    embedding_created_at = :now
                WHERE id = :chunk_id
                """
            ),
            {
                "chunk_id": str(chunk_id),
                "embedding": embedding_literal(embedding),
                "embedding_provider": embedding_provider,
                "embedding_model": embedding_model,
                "embedding_dimension": embedding_dimension,
                "now": now,
            },
        )


async def mark_ready(session: AsyncSession, document_id: UUID) -> None:
    await session.execute(
        text(
            """
            UPDATE documents
            SET status = 'ready',
                failure_code = NULL,
                failure_reason = NULL,
                processed_at = :now,
                updated_at = :now
            WHERE id = :document_id AND deleted_at IS NULL
            """
        ),
        {"document_id": str(document_id), "now": datetime.now(UTC)},
    )


async def mark_failed(
    session: AsyncSession,
    *,
    document_id: UUID,
    failure_code: str,
    failure_reason: str,
) -> None:
    now = datetime.now(UTC)
    await session.execute(
        text("DELETE FROM document_chunks WHERE document_id = :document_id"),
        {"document_id": str(document_id)},
    )
    await session.execute(
        text(
            """
            UPDATE documents
            SET status = 'failed',
                failure_code = :failure_code,
                failure_reason = :failure_reason,
                updated_at = :now
            WHERE id = :document_id AND deleted_at IS NULL
            """
        ),
        {
            "document_id": str(document_id),
            "failure_code": failure_code,
            "failure_reason": failure_reason[:300],
            "now": now,
        },
    )


async def queue_failed_document(
    session: AsyncSession,
    *,
    user_id: UUID,
    document_id: UUID,
) -> DocumentResponse | None:
    result = await session.execute(
        text(
            """
            UPDATE documents
            SET status = 'queued',
                failure_code = NULL,
                failure_reason = NULL,
                processing_started_at = NULL,
                updated_at = :now
            WHERE id = :document_id
              AND user_id = :user_id
              AND deleted_at IS NULL
              AND status = 'failed'
            RETURNING id, user_id, original_filename, storage_key, mime_type, size_bytes,
              checksum_sha256, status, page_count, extracted_character_count,
              failure_code, failure_reason, created_at, updated_at, processed_at, deleted_at
            """
        ),
        {"document_id": str(document_id), "user_id": str(user_id), "now": datetime.now(UTC)},
    )
    row = result.mappings().one_or_none()
    return document_response_from_row(row) if row is not None else None


async def soft_delete_document(
    session: AsyncSession,
    *,
    user_id: UUID,
    document_id: UUID,
) -> DocumentRecord | None:
    result = await session.execute(
        text(
            """
            UPDATE documents
            SET status = 'deleted',
                deleted_at = :now,
                updated_at = :now
            WHERE id = :document_id AND user_id = :user_id AND deleted_at IS NULL
            RETURNING id, user_id, original_filename, storage_key, mime_type, size_bytes,
              checksum_sha256, status, page_count, extracted_character_count,
              failure_code, failure_reason, created_at, updated_at, processed_at, deleted_at
            """
        ),
        {"document_id": str(document_id), "user_id": str(user_id), "now": datetime.now(UTC)},
    )
    row = result.mappings().one_or_none()
    if row is None:
        return None
    await session.execute(
        text("DELETE FROM document_chunks WHERE document_id = :document_id"),
        {"document_id": str(document_id)},
    )
    return document_record_from_row(row)
