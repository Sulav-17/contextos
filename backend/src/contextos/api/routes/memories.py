from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError

from contextos.api.dependencies import AuthContext, require_auth
from contextos.api.errors import ContextOSError
from contextos.auth.errors import AI_PROVIDER_UNAVAILABLE, MEMORY_DUPLICATE, MEMORY_NOT_FOUND
from contextos.domain.ai import ProviderError
from contextos.domain.memories import (
    MemoryCreateRequest,
    MemoryListResponse,
    MemoryResponse,
    MemoryStatus,
    MemoryUpdateRequest,
    approve_memory,
    create_manual_memory,
    delete_memory,
    disable_memory,
    enable_memory,
    list_memories,
    reject_memory,
    update_memory,
)

router = APIRouter(tags=["memories"])
AUTH_CONTEXT = Depends(require_auth)
NO_STORE_HEADERS = {"Cache-Control": "private, no-store"}
MEMORY_STATUS_QUERY = Query(default=None)


@router.post("/api/v1/memories", status_code=201, response_model=MemoryResponse)
async def create_memory_route(
    request: MemoryCreateRequest,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await create_manual_memory(
            context.session, user_id=context.user.id, request=request, settings=context.settings
        )
    except ProviderError as exc:
        raise ContextOSError(AI_PROVIDER_UNAVAILABLE) from exc
    except IntegrityError as exc:
        raise ContextOSError(MEMORY_DUPLICATE) from exc


@router.get("/api/v1/memories", response_model=MemoryListResponse)
async def list_memories_route(
    response: Response,
    status: MemoryStatus | None = MEMORY_STATUS_QUERY,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await list_memories(context.session, user_id=context.user.id, status=status)


@router.get("/api/v1/memories/suggestions", response_model=MemoryListResponse)
async def list_memory_suggestions_route(
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await list_memories(context.session, user_id=context.user.id, status="suggested")


@router.patch("/api/v1/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory_route(
    memory_id: UUID,
    request: MemoryUpdateRequest,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        memory = await update_memory(
            context.session,
            user_id=context.user.id,
            memory_id=memory_id,
            request=request,
            settings=context.settings,
        )
    except ProviderError as exc:
        raise ContextOSError(AI_PROVIDER_UNAVAILABLE) from exc
    except IntegrityError as exc:
        raise ContextOSError(MEMORY_DUPLICATE) from exc
    if memory is None:
        raise ContextOSError(MEMORY_NOT_FOUND)
    return memory


@router.post("/api/v1/memories/{memory_id}/approve", response_model=MemoryResponse)
async def approve_memory_route(
    memory_id: UUID,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        memory = await approve_memory(
            context.session, user_id=context.user.id, memory_id=memory_id, settings=context.settings
        )
    except ProviderError as exc:
        raise ContextOSError(AI_PROVIDER_UNAVAILABLE) from exc
    if memory is None:
        raise ContextOSError(MEMORY_NOT_FOUND)
    return memory


@router.post("/api/v1/memories/{memory_id}/reject", response_model=MemoryResponse)
async def reject_memory_route(
    memory_id: UUID,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryResponse:
    response.headers["Cache-Control"] = "private, no-store"
    memory = await reject_memory(context.session, user_id=context.user.id, memory_id=memory_id)
    if memory is None:
        raise ContextOSError(MEMORY_NOT_FOUND)
    return memory


@router.post("/api/v1/memories/{memory_id}/disable", response_model=MemoryResponse)
async def disable_memory_route(
    memory_id: UUID,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryResponse:
    response.headers["Cache-Control"] = "private, no-store"
    memory = await disable_memory(context.session, user_id=context.user.id, memory_id=memory_id)
    if memory is None:
        raise ContextOSError(MEMORY_NOT_FOUND)
    return memory


@router.post("/api/v1/memories/{memory_id}/enable", response_model=MemoryResponse)
async def enable_memory_route(
    memory_id: UUID,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MemoryResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        memory = await enable_memory(
            context.session, user_id=context.user.id, memory_id=memory_id, settings=context.settings
        )
    except ProviderError as exc:
        raise ContextOSError(AI_PROVIDER_UNAVAILABLE) from exc
    if memory is None:
        raise ContextOSError(MEMORY_NOT_FOUND)
    return memory


@router.delete("/api/v1/memories/{memory_id}", status_code=204)
async def delete_memory_route(
    memory_id: UUID,
    context: AuthContext = AUTH_CONTEXT,
) -> Response:
    deleted = await delete_memory(context.session, user_id=context.user.id, memory_id=memory_id)
    if not deleted:
        raise ContextOSError(MEMORY_NOT_FOUND)
    return Response(status_code=204, headers=NO_STORE_HEADERS)
