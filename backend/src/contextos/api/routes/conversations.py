from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from contextos.api.dependencies import AuthContext, require_auth
from contextos.api.errors import ContextOSError
from contextos.auth.errors import (
    AI_DAILY_LIMIT_REACHED,
    AI_MONTHLY_LIMIT_REACHED,
    AI_PROVIDER_UNAVAILABLE,
    CONVERSATION_NOT_FOUND,
    DOCUMENT_NOT_FOUND,
)
from contextos.domain.ai import ProviderError
from contextos.domain.chat import (
    ConversationCreateRequest,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationSummary,
    ConversationUpdateRequest,
    MessageCreateRequest,
    MessageCreateResponse,
    UsageResponse,
    create_conversation,
    delete_conversation,
    get_conversation_detail,
    list_conversations,
    submit_question,
    update_conversation_title,
    usage_status,
)

router = APIRouter(tags=["conversations"])
AUTH_CONTEXT = Depends(require_auth)
NO_STORE_HEADERS = {"Cache-Control": "private, no-store"}


@router.post("/api/v1/conversations", status_code=201, response_model=ConversationSummary)
async def create_conversation_route(
    request: ConversationCreateRequest,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> ConversationSummary:
    response.headers["Cache-Control"] = "private, no-store"
    return await create_conversation(context.session, user_id=context.user.id, title=request.title)


@router.get("/api/v1/conversations", response_model=ConversationListResponse)
async def list_conversations_route(
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> ConversationListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await list_conversations(context.session, context.user.id)


@router.get("/api/v1/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_route(
    conversation_id: UUID,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> ConversationDetailResponse:
    response.headers["Cache-Control"] = "private, no-store"
    conversation = await get_conversation_detail(
        context.session, user_id=context.user.id, conversation_id=conversation_id
    )
    if conversation is None:
        raise ContextOSError(CONVERSATION_NOT_FOUND)
    return conversation


@router.patch("/api/v1/conversations/{conversation_id}", response_model=ConversationSummary)
async def update_conversation_route(
    conversation_id: UUID,
    request: ConversationUpdateRequest,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> ConversationSummary:
    response.headers["Cache-Control"] = "private, no-store"
    conversation = await update_conversation_title(
        context.session,
        user_id=context.user.id,
        conversation_id=conversation_id,
        title=request.title,
    )
    if conversation is None:
        raise ContextOSError(CONVERSATION_NOT_FOUND)
    return conversation


@router.post(
    "/api/v1/conversations/{conversation_id}/messages",
    response_model=MessageCreateResponse,
)
async def submit_message_route(
    conversation_id: UUID,
    request: MessageCreateRequest,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MessageCreateResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        result = await submit_question(
            context.session,
            user_id=context.user.id,
            conversation_id=conversation_id,
            request=request,
            settings=context.settings,
        )
    except PermissionError as exc:
        if str(exc) == "daily_ai_message_limit_reached":
            raise ContextOSError(AI_DAILY_LIMIT_REACHED) from exc
        raise ContextOSError(AI_MONTHLY_LIMIT_REACHED) from exc
    except ProviderError as exc:
        raise ContextOSError(AI_PROVIDER_UNAVAILABLE) from exc
    except ValueError as exc:
        raise ContextOSError(DOCUMENT_NOT_FOUND) from exc
    if result is None:
        raise ContextOSError(CONVERSATION_NOT_FOUND)
    return result


@router.delete("/api/v1/conversations/{conversation_id}", status_code=204)
async def delete_conversation_route(
    conversation_id: UUID,
    context: AuthContext = AUTH_CONTEXT,
) -> Response:
    deleted = await delete_conversation(
        context.session, user_id=context.user.id, conversation_id=conversation_id
    )
    if not deleted:
        raise ContextOSError(CONVERSATION_NOT_FOUND)
    return Response(status_code=204, headers=NO_STORE_HEADERS)


@router.get("/api/v1/usage", response_model=UsageResponse)
async def usage_route(
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> UsageResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await usage_status(context.session, user_id=context.user.id, settings=context.settings)
