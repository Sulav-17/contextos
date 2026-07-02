from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from contextos.core.config import Settings
from contextos.domain.chat import UsageResponse, usage_status

RECENT_LIMIT = 5


class DashboardCounts(BaseModel):
    active_documents: int
    active_conversations: int
    approved_memories: int
    pending_suggestions: int


class DashboardConversation(BaseModel):
    id: UUID
    title: str
    updated_at: datetime
    archived_at: datetime | None = None


class DashboardDocument(BaseModel):
    id: UUID
    original_filename: str
    status: str
    created_at: datetime
    updated_at: datetime


class DashboardMemory(BaseModel):
    id: UUID
    memory_type: str
    content: str
    status: str
    source_conversation_id: UUID | None = None
    source_conversation_title: str | None = None
    updated_at: datetime


class DashboardResponse(BaseModel):
    counts: DashboardCounts
    usage: UsageResponse
    recent_conversations: list[DashboardConversation] = Field(default_factory=list)
    recent_documents: list[DashboardDocument] = Field(default_factory=list)
    recent_memories: list[DashboardMemory] = Field(default_factory=list)
    pending_suggestions: list[DashboardMemory] = Field(default_factory=list)


async def get_dashboard(
    session: AsyncSession,
    *,
    user_id: UUID,
    settings: Settings,
) -> DashboardResponse:
    counts_result = await session.execute(
        text(
            """
            SELECT
              (
                SELECT count(*)
                FROM documents
                WHERE user_id = :user_id
                  AND deleted_at IS NULL
                  AND status <> 'deleted'
              ) AS active_documents,
              (
                SELECT count(*)
                FROM conversations
                WHERE user_id = :user_id
                  AND deleted_at IS NULL
                  AND archived_at IS NULL
              ) AS active_conversations,
              (
                SELECT count(*)
                FROM memories
                WHERE user_id = :user_id
                  AND deleted_at IS NULL
                  AND status = 'approved'
              ) AS approved_memories,
              (
                SELECT count(*)
                FROM memories
                WHERE user_id = :user_id
                  AND deleted_at IS NULL
                  AND status = 'suggested'
              ) AS pending_suggestions
            """
        ),
        {"user_id": str(user_id)},
    )
    counts = DashboardCounts.model_validate(dict(counts_result.mappings().one()))
    usage = await usage_status(session, user_id=user_id, settings=settings)
    recent_conversations = await _recent_conversations(session, user_id=user_id)
    recent_documents = await _recent_documents(session, user_id=user_id)
    recent_memories = await _recent_memories(session, user_id=user_id, status="approved")
    pending_suggestions = await _recent_memories(session, user_id=user_id, status="suggested")
    return DashboardResponse(
        counts=counts,
        usage=usage,
        recent_conversations=recent_conversations,
        recent_documents=recent_documents,
        recent_memories=recent_memories,
        pending_suggestions=pending_suggestions,
    )


async def _recent_conversations(
    session: AsyncSession, *, user_id: UUID
) -> list[DashboardConversation]:
    result = await session.execute(
        text(
            """
            SELECT id, title, updated_at, archived_at
            FROM conversations
            WHERE user_id = :user_id
              AND deleted_at IS NULL
            ORDER BY updated_at DESC, id DESC
            LIMIT :limit
            """
        ),
        {"user_id": str(user_id), "limit": RECENT_LIMIT},
    )
    return [DashboardConversation.model_validate(dict(row)) for row in result.mappings()]


async def _recent_documents(session: AsyncSession, *, user_id: UUID) -> list[DashboardDocument]:
    result = await session.execute(
        text(
            """
            SELECT id, original_filename, status, created_at, updated_at
            FROM documents
            WHERE user_id = :user_id
              AND deleted_at IS NULL
              AND status <> 'deleted'
            ORDER BY updated_at DESC, id DESC
            LIMIT :limit
            """
        ),
        {"user_id": str(user_id), "limit": RECENT_LIMIT},
    )
    return [DashboardDocument.model_validate(dict(row)) for row in result.mappings()]


async def _recent_memories(
    session: AsyncSession, *, user_id: UUID, status: str
) -> list[DashboardMemory]:
    result = await session.execute(
        text(
            """
            SELECT m.id,
                   m.memory_type,
                   m.content,
                   m.status,
                   m.source_conversation_id,
                   c.title AS source_conversation_title,
                   m.updated_at
            FROM memories m
            LEFT JOIN conversations c
              ON c.id = m.source_conversation_id
             AND c.user_id = m.user_id
             AND c.deleted_at IS NULL
            WHERE m.user_id = :user_id
              AND m.deleted_at IS NULL
              AND m.status = :status
            ORDER BY m.updated_at DESC, m.id DESC
            LIMIT :limit
            """
        ),
        {"user_id": str(user_id), "status": status, "limit": RECENT_LIMIT},
    )
    return [DashboardMemory.model_validate(dict(row)) for row in result.mappings()]
