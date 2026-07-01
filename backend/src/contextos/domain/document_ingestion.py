from __future__ import annotations

import asyncio
import re
from io import BytesIO
from uuid import UUID

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from redis import Redis
from rq import Queue
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from contextos.core.config import Settings, get_settings
from contextos.domain.ai import ProviderError, build_embedding_provider
from contextos.domain.documents import (
    get_document_for_worker,
    list_chunks_needing_embeddings,
    mark_failed,
    mark_processing,
    mark_ready,
    replace_chunks,
    store_chunk_embeddings,
)
from contextos.infrastructure.document_storage import LocalDocumentStorage
from contextos.infrastructure.tenant_context import set_tenant_context


class IngestionFailure(Exception):
    def __init__(self, code: str, reason: str) -> None:
        super().__init__(code)
        self.code = code
        self.reason = reason


def count_pdf_pages(content: bytes) -> int:
    try:
        reader = PdfReader(BytesIO(content))
        return len(reader.pages)
    except (PdfReadError, OSError, ValueError) as exc:
        raise IngestionFailure("invalid_pdf", "The PDF could not be read.") from exc


def normalize_extracted_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def chunk_pages(
    pages: list[tuple[int, str]],
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[tuple[int, int, str]]:
    chunks: list[tuple[int, int, str]] = []
    for page_number, page_text in pages:
        if not page_text:
            continue
        start = 0
        while start < len(page_text):
            end = min(start + chunk_size, len(page_text))
            content = page_text[start:end].strip()
            if content:
                chunks.append((len(chunks), page_number, content))
            if end == len(page_text):
                break
            start = max(end - chunk_overlap, start + 1)
    return chunks


def extract_pdf_chunks(
    content: bytes,
    *,
    max_pages: int,
    chunk_size: int,
    chunk_overlap: int,
) -> tuple[int, int, list[tuple[int, int, str]]]:
    try:
        reader = PdfReader(BytesIO(content))
        page_count = len(reader.pages)
        if page_count > max_pages:
            raise IngestionFailure("page_limit_exceeded", "The PDF has too many pages.")
        pages: list[tuple[int, str]] = []
        extracted_character_count = 0
        for index, page in enumerate(reader.pages, start=1):
            page_text = normalize_extracted_text(page.extract_text() or "")
            extracted_character_count += len(page_text)
            pages.append((index, page_text))
    except IngestionFailure:
        raise
    except (PdfReadError, OSError, ValueError) as exc:
        raise IngestionFailure("invalid_pdf", "The PDF could not be read.") from exc

    chunks = chunk_pages(pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        raise IngestionFailure("no_extractable_text", "The PDF does not contain extractable text.")
    return page_count, extracted_character_count, chunks


def enqueue_document(settings: Settings, document_id: UUID) -> None:
    redis = Redis.from_url(settings.redis_url.get_secret_value())
    queue = Queue(settings.document_queue_name, connection=redis)
    queue.enqueue(
        "contextos.domain.document_ingestion.process_document_job",
        str(document_id),
        job_timeout=300,
    )


async def process_document(document_id: UUID, settings: Settings) -> None:
    engine = create_async_engine(settings.database_url.get_secret_value(), pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    storage = LocalDocumentStorage(settings)
    try:
        async with factory() as session:
            async with session.begin():
                await set_tenant_context(session, document_id, "worker")
                document = await get_document_for_worker(session, document_id)
                if document is None or document.status == "deleted":
                    return
                if document.status == "ready":
                    return
                should_process = await mark_processing(session, document_id)
                if not should_process:
                    return

        try:
            path = storage.read_path(document.storage_key)
            content = path.read_bytes()
            page_count, character_count, chunks = extract_pdf_chunks(
                content,
                max_pages=settings.document_max_pages,
                chunk_size=settings.document_chunk_size,
                chunk_overlap=settings.document_chunk_overlap,
            )
        except IngestionFailure as failure:
            async with factory() as session:
                async with session.begin():
                    await set_tenant_context(session, document_id, "worker")
                    await mark_failed(
                        session,
                        document_id=document_id,
                        failure_code=failure.code,
                        failure_reason=failure.reason,
                    )
            return
        except FileNotFoundError:
            async with factory() as session:
                async with session.begin():
                    await set_tenant_context(session, document_id, "worker")
                    await mark_failed(
                        session,
                        document_id=document_id,
                        failure_code="file_missing",
                        failure_reason="The stored PDF could not be found.",
                    )
            return

        async with factory() as session:
            async with session.begin():
                await set_tenant_context(session, document_id, "worker")
                await replace_chunks(
                    session,
                    document_id=document_id,
                    user_id=document.user_id,
                    chunks=chunks,
                    page_count=page_count,
                    extracted_character_count=character_count,
                )

        embedding_provider = build_embedding_provider(settings)
        try:
            async with factory() as session:
                async with session.begin():
                    await set_tenant_context(session, document_id, "worker")
                    chunks_to_embed = await list_chunks_needing_embeddings(
                        session,
                        document_id=document_id,
                        embedding_provider=embedding_provider.provider,
                        embedding_model=embedding_provider.model,
                        embedding_dimension=embedding_provider.dimension,
                    )
            for start in range(0, len(chunks_to_embed), 16):
                batch = chunks_to_embed[start : start + 16]
                vectors = await embedding_provider.embed([content for _, content in batch])
                async with factory() as session:
                    async with session.begin():
                        await set_tenant_context(session, document_id, "worker")
                        await store_chunk_embeddings(
                            session,
                            embeddings=[
                                (chunk_id, vector)
                                for (chunk_id, _content), vector in zip(batch, vectors, strict=True)
                            ],
                            embedding_provider=embedding_provider.provider,
                            embedding_model=embedding_provider.model,
                            embedding_dimension=embedding_provider.dimension,
                        )
            async with factory() as session:
                async with session.begin():
                    await set_tenant_context(session, document_id, "worker")
                    await mark_ready(session, document_id)
        except ProviderError:
            async with factory() as session:
                async with session.begin():
                    await set_tenant_context(session, document_id, "worker")
                    await mark_failed(
                        session,
                        document_id=document_id,
                        failure_code="embedding_failed",
                        failure_reason="Document text could not be embedded.",
                    )
    finally:
        await engine.dispose()


def process_document_job(document_id: str) -> None:
    settings = get_settings()
    asyncio.run(process_document(UUID(document_id), settings))
