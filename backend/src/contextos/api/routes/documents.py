from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import FileResponse, Response

from contextos.api.dependencies import AuthContext, require_auth
from contextos.api.errors import ContextOSError
from contextos.auth.errors import (
    DOCUMENT_INVALID_FILE,
    DOCUMENT_LIMIT_REACHED,
    DOCUMENT_NOT_FOUND,
    DOCUMENT_NOT_RETRYABLE,
    DOCUMENT_STORAGE_LIMIT_REACHED,
    DOCUMENT_TOO_LARGE,
    DOCUMENT_TOO_MANY_PAGES,
    PROVIDER_UNAVAILABLE,
)
from contextos.domain.document_ingestion import IngestionFailure, count_pdf_pages, enqueue_document
from contextos.domain.documents import (
    DocumentListResponse,
    DocumentResponse,
    count_active_documents,
    create_queued_document,
    get_document,
    list_documents,
    queue_failed_document,
    sanitize_filename,
    soft_delete_document,
    total_active_document_size,
)
from contextos.infrastructure.document_storage import (
    LocalDocumentStorage,
    SupabaseStorageError,
    build_document_storage,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
AUTH_CONTEXT = Depends(require_auth)
PDF_UPLOAD = File(...)
PDF_MIME_TYPES = {"application/pdf", "application/x-pdf"}
NO_STORE_HEADERS = {"Cache-Control": "private, no-store"}


def _validate_filename(filename: str) -> str:
    sanitized = sanitize_filename(filename)
    if not sanitized.casefold().endswith(".pdf"):
        raise ContextOSError(DOCUMENT_INVALID_FILE)
    return sanitized


async def _read_pdf_upload(file: UploadFile, max_size_bytes: int) -> bytes:
    if file.content_type not in PDF_MIME_TYPES:
        raise ContextOSError(DOCUMENT_INVALID_FILE)
    content = await file.read(max_size_bytes + 1)
    if not content:
        raise ContextOSError(DOCUMENT_INVALID_FILE)
    if len(content) > max_size_bytes:
        raise ContextOSError(DOCUMENT_TOO_LARGE)
    if not content.startswith(b"%PDF-"):
        raise ContextOSError(DOCUMENT_INVALID_FILE)
    return content


def _enqueue_later(
    background_tasks: BackgroundTasks, context: AuthContext, document_id: UUID
) -> None:
    background_tasks.add_task(enqueue_document, context.settings, document_id)


@router.post("", status_code=201, response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    response: Response,
    file: UploadFile = PDF_UPLOAD,
    context: AuthContext = AUTH_CONTEXT,
) -> DocumentResponse:
    response.headers["Cache-Control"] = "private, no-store"
    settings = context.settings
    filename = _validate_filename(file.filename or "document.pdf")
    content = await _read_pdf_upload(file, settings.document_max_pdf_size_bytes)
    try:
        page_count = count_pdf_pages(content)
    except IngestionFailure as exc:
        raise ContextOSError(DOCUMENT_INVALID_FILE) from exc
    if page_count > settings.document_max_pages:
        raise ContextOSError(DOCUMENT_TOO_MANY_PAGES)
    if (
        await count_active_documents(context.session, context.user.id)
        >= settings.document_max_per_user
    ):
        raise ContextOSError(DOCUMENT_LIMIT_REACHED)
    total_size = await total_active_document_size(context.session, context.user.id)
    if total_size + len(content) > settings.document_max_total_size_bytes:
        raise ContextOSError(DOCUMENT_STORAGE_LIMIT_REACHED)

    storage = build_document_storage(settings)
    try:
        stored = storage.write(content, user_id=context.user.id)
    except SupabaseStorageError as exc:
        raise ContextOSError(PROVIDER_UNAVAILABLE) from exc
    try:
        document = await create_queued_document(
            context.session,
            user_id=context.user.id,
            original_filename=filename,
            storage_key=stored.storage_key,
            mime_type="application/pdf",
            size_bytes=stored.size_bytes,
            checksum_sha256=stored.checksum_sha256,
            page_count=page_count,
        )
    except Exception:
        try:
            storage.delete(stored.storage_key)
        except SupabaseStorageError as delete_exc:
            raise ContextOSError(PROVIDER_UNAVAILABLE) from delete_exc
        raise
    _enqueue_later(background_tasks, context, document.id)
    return document


@router.get("", response_model=DocumentListResponse)
async def read_documents(
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> DocumentListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await list_documents(context.session, context.user.id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(
    document_id: UUID,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> DocumentResponse:
    response.headers["Cache-Control"] = "private, no-store"
    document = await get_document(context.session, user_id=context.user.id, document_id=document_id)
    if document is None:
        raise ContextOSError(DOCUMENT_NOT_FOUND)
    return DocumentResponse.model_validate(document.model_dump())


@router.get("/{document_id}/download", response_model=None)
async def download_document(
    document_id: UUID,
    context: AuthContext = AUTH_CONTEXT,
) -> Response:
    settings = context.settings
    document = await get_document(context.session, user_id=context.user.id, document_id=document_id)
    if document is None:
        raise ContextOSError(DOCUMENT_NOT_FOUND)
    storage = build_document_storage(settings)
    if isinstance(storage, LocalDocumentStorage):
        path = storage.read_path(document.storage_key)
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=document.original_filename,
            headers=NO_STORE_HEADERS,
        )
    try:
        content = storage.read_bytes(document.storage_key)
    except SupabaseStorageError as exc:
        raise ContextOSError(PROVIDER_UNAVAILABLE) from exc
    headers = {
        **NO_STORE_HEADERS,
        "Content-Disposition": f'attachment; filename="{document.original_filename}"',
    }
    return Response(content=content, media_type="application/pdf", headers=headers)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    context: AuthContext = AUTH_CONTEXT,
) -> Response:
    settings = context.settings
    document = await soft_delete_document(
        context.session, user_id=context.user.id, document_id=document_id
    )
    if document is None:
        raise ContextOSError(DOCUMENT_NOT_FOUND)
    try:
        build_document_storage(settings).delete(document.storage_key)
    except SupabaseStorageError as exc:
        raise ContextOSError(PROVIDER_UNAVAILABLE) from exc
    return Response(status_code=204, headers=NO_STORE_HEADERS)


@router.post("/{document_id}/retry", response_model=DocumentResponse)
async def retry_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> DocumentResponse:
    response.headers["Cache-Control"] = "private, no-store"
    current = await get_document(context.session, user_id=context.user.id, document_id=document_id)
    if current is None:
        raise ContextOSError(DOCUMENT_NOT_FOUND)
    document = await queue_failed_document(
        context.session, user_id=context.user.id, document_id=document_id
    )
    if document is None:
        raise ContextOSError(DOCUMENT_NOT_RETRYABLE)
    _enqueue_later(background_tasks, context, document.id)
    return document
