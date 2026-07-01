from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Literal, cast
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from contextos.core.config import Settings
from contextos.domain.ai import (
    ChatRequest,
    ProviderError,
    build_chat_provider,
    build_embedding_provider,
)

MessageRole = Literal["user", "assistant"]
EvidenceStatus = Literal["grounded", "insufficient_evidence"]
FALLBACK_ANSWER = "I could not find enough evidence in your documents to answer that."


class ConversationCreateRequest(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=120)


class ConversationSummary(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]


class CitationResponse(BaseModel):
    citation_index: int
    document_id: UUID
    document_name: str
    page_number: int
    excerpt: str


class MessageResponse(BaseModel):
    id: UUID
    role: MessageRole
    content: str
    status: str
    created_at: datetime
    citations: list[CitationResponse] = Field(default_factory=list)


class ConversationDetailResponse(ConversationSummary):
    messages: list[MessageResponse]


class MessageCreateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[UUID] = Field(default_factory=list, max_length=20)


class MessageCreateResponse(BaseModel):
    message: MessageResponse
    usage: UsageResponse
    evidence_status: EvidenceStatus


class UsageBucket(BaseModel):
    used: int
    limit: int
    remaining: int


class UsageResponse(BaseModel):
    daily: UsageBucket
    monthly: UsageBucket


class RetrievedChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: UUID
    document_id: UUID
    document_name: str
    page_number: int
    content: str
    distance: float

    @property
    def similarity(self) -> float:
        return 1.0 - self.distance


@dataclass(frozen=True, slots=True)
class UsagePeriods:
    daily_start: date
    monthly_start: date


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


def usage_periods(now: datetime | None = None) -> UsagePeriods:
    current = now or datetime.now(UTC)
    return UsagePeriods(daily_start=current.date(), monthly_start=current.date().replace(day=1))


async def create_conversation(
    session: AsyncSession, *, user_id: UUID, title: str
) -> ConversationSummary:
    result = await session.execute(
        text(
            """
            INSERT INTO conversations (user_id, title)
            VALUES (:user_id, :title)
            RETURNING id, title, created_at, updated_at
            """
        ),
        {"user_id": str(user_id), "title": title.strip()[:120] or "New conversation"},
    )
    return ConversationSummary.model_validate(dict(result.mappings().one()))


async def list_conversations(session: AsyncSession, user_id: UUID) -> ConversationListResponse:
    result = await session.execute(
        text(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = :user_id AND deleted_at IS NULL
            ORDER BY updated_at DESC, id DESC
            """
        ),
        {"user_id": str(user_id)},
    )
    return ConversationListResponse(
        conversations=[ConversationSummary.model_validate(dict(row)) for row in result.mappings()]
    )


async def get_conversation_detail(
    session: AsyncSession, *, user_id: UUID, conversation_id: UUID
) -> ConversationDetailResponse | None:
    summary = await _get_conversation(session, user_id=user_id, conversation_id=conversation_id)
    if summary is None:
        return None
    result = await session.execute(
        text(
            """
            SELECT id, role, content, status, created_at
            FROM messages
            WHERE user_id = :user_id AND conversation_id = :conversation_id
            ORDER BY created_at ASC, id ASC
            """
        ),
        {"user_id": str(user_id), "conversation_id": str(conversation_id)},
    )
    messages = [MessageResponse.model_validate(dict(row)) for row in result.mappings()]
    citations = await _citations_for_messages(session, user_id=user_id, messages=messages)
    return ConversationDetailResponse(
        **summary.model_dump(),
        messages=[
            message.model_copy(update={"citations": citations.get(message.id, [])})
            for message in messages
        ],
    )


async def delete_conversation(
    session: AsyncSession, *, user_id: UUID, conversation_id: UUID
) -> bool:
    result = await session.execute(
        text(
            """
            UPDATE conversations
            SET deleted_at = :now, updated_at = :now
            WHERE id = :conversation_id AND user_id = :user_id AND deleted_at IS NULL
            """
        ),
        {
            "conversation_id": str(conversation_id),
            "user_id": str(user_id),
            "now": datetime.now(UTC),
        },
    )
    return cast(CursorResult[object], result).rowcount == 1


async def usage_status(
    session: AsyncSession, *, user_id: UUID, settings: Settings
) -> UsageResponse:
    counts = await _usage_counts(session, user_id=user_id)
    return _usage_response(
        daily_used=counts["daily"],
        monthly_used=counts["monthly"],
        settings=settings,
    )


async def submit_question(
    session: AsyncSession,
    *,
    user_id: UUID,
    conversation_id: UUID,
    request: MessageCreateRequest,
    settings: Settings,
) -> MessageCreateResponse | None:
    conversation = await _get_conversation(
        session, user_id=user_id, conversation_id=conversation_id
    )
    if conversation is None:
        return None
    await _validate_document_filter(session, user_id=user_id, document_ids=request.document_ids)
    usage = await _increment_usage_or_raise(session, user_id=user_id, settings=settings)
    user_message_id = await _insert_message(
        session,
        user_id=user_id,
        conversation_id=conversation_id,
        role="user",
        content=request.question.strip(),
        status="accepted",
    )
    embedding_provider = build_embedding_provider(settings)
    try:
        query_embedding = (await embedding_provider.embed([request.question.strip()]))[0]
        chunks = await retrieve_chunks(
            session,
            user_id=user_id,
            query_embedding=query_embedding,
            settings=settings,
            document_ids=request.document_ids,
        )
        if not chunks:
            assistant_id = await _insert_message(
                session,
                user_id=user_id,
                conversation_id=conversation_id,
                role="assistant",
                content=FALLBACK_ANSWER,
                status="completed",
            )
            return MessageCreateResponse(
                message=MessageResponse(
                    id=assistant_id,
                    role="assistant",
                    content=FALLBACK_ANSWER,
                    status="completed",
                    created_at=datetime.now(UTC),
                    citations=[],
                ),
                usage=usage,
                evidence_status="insufficient_evidence",
            )
        chat_provider = build_chat_provider(settings)
        chat_result = await chat_provider.generate(
            _build_chat_request(request.question, chunks, settings)
        )
        answer = chat_result.content.strip() or FALLBACK_ANSWER
        if answer == FALLBACK_ANSWER:
            chunks = []
        assistant_id = await _insert_message(
            session,
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            status="completed",
            provider=chat_result.provider,
            model=chat_result.model,
        )
        citations = await _insert_citations(
            session,
            user_id=user_id,
            message_id=assistant_id,
            chunks=chunks,
        )
        await session.execute(
            text("UPDATE conversations SET updated_at = :now WHERE id = :conversation_id"),
            {"conversation_id": str(conversation_id), "now": datetime.now(UTC)},
        )
        return MessageCreateResponse(
            message=MessageResponse(
                id=assistant_id,
                role="assistant",
                content=answer,
                status="completed",
                created_at=datetime.now(UTC),
                citations=citations,
            ),
            usage=usage,
            evidence_status="grounded" if citations else "insufficient_evidence",
        )
    except ProviderError as exc:
        await _insert_message(
            session,
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content="The AI provider is temporarily unavailable.",
            status="failed",
            error_code=exc.code,
        )
        raise
    finally:
        _ = user_message_id


async def retrieve_chunks(
    session: AsyncSession,
    *,
    user_id: UUID,
    query_embedding: list[float],
    settings: Settings,
    document_ids: list[UUID],
) -> list[RetrievedChunk]:
    params: dict[str, object] = {
        "user_id": str(user_id),
        "embedding": vector_literal(query_embedding),
        "provider": settings.embedding_provider,
        "model": settings.embedding_model,
        "dimension": settings.embedding_dimension,
        "threshold": settings.retrieval_similarity_threshold,
        "limit": settings.retrieval_top_k,
    }
    filter_sql = ""
    if document_ids:
        params["document_ids"] = [str(document_id) for document_id in document_ids]
        filter_sql = "AND c.document_id = ANY(:document_ids)"
    result = await session.execute(
        text(
            f"""
            SELECT c.id AS chunk_id,
                   c.document_id,
                   d.original_filename AS document_name,
                   c.page_number,
                   c.content,
                   c.embedding <=> CAST(:embedding AS vector) AS distance
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id AND d.user_id = c.user_id
            WHERE c.user_id = :user_id
              AND d.status = 'ready'
              AND d.deleted_at IS NULL
              AND c.embedding IS NOT NULL
              AND c.embedding_provider = :provider
              AND c.embedding_model = :model
              AND c.embedding_dimension = :dimension
              {filter_sql}
              AND 1 - (c.embedding <=> CAST(:embedding AS vector)) >= :threshold
            ORDER BY c.embedding <=> CAST(:embedding AS vector), d.created_at, c.chunk_index
            LIMIT :limit
            """
        ),
        params,
    )
    return [RetrievedChunk.model_validate(dict(row)) for row in result.mappings()]


def _build_chat_request(
    question: str, chunks: list[RetrievedChunk], settings: Settings
) -> ChatRequest:
    context_parts: list[str] = []
    remaining = settings.retrieval_max_context_characters
    for index, chunk in enumerate(chunks, start=1):
        excerpt = chunk.content[: min(len(chunk.content), remaining)]
        if not excerpt:
            break
        context_parts.append(
            f"[{index}] {chunk.document_name}, page {chunk.page_number}: {excerpt}"
        )
        remaining -= len(excerpt)
    context_text = "\n\n".join(context_parts)
    return ChatRequest(
        system_prompt=(
            "Answer only from the supplied ContextOS document context. "
            "If the context is insufficient, say exactly that there is not enough evidence. "
            "Do not invent document titles, page numbers, or unsupported facts."
        ),
        user_prompt=f"Context:\n{context_text}\n\nQuestion: {question}",
    )


async def _get_conversation(
    session: AsyncSession, *, user_id: UUID, conversation_id: UUID
) -> ConversationSummary | None:
    result = await session.execute(
        text(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            WHERE id = :conversation_id AND user_id = :user_id AND deleted_at IS NULL
            """
        ),
        {"conversation_id": str(conversation_id), "user_id": str(user_id)},
    )
    row = result.mappings().one_or_none()
    return ConversationSummary.model_validate(dict(row)) if row is not None else None


async def _citations_for_messages(
    session: AsyncSession, *, user_id: UUID, messages: list[MessageResponse]
) -> dict[UUID, list[CitationResponse]]:
    if not messages:
        return {}
    result = await session.execute(
        text(
            """
            SELECT mc.message_id,
                   mc.citation_index,
                   mc.document_id,
                   d.original_filename AS document_name,
                   mc.page_number,
                   mc.excerpt
            FROM message_citations mc
            JOIN documents d ON d.id = mc.document_id AND d.user_id = mc.user_id
            WHERE mc.user_id = :user_id AND mc.message_id = ANY(:message_ids)
            ORDER BY mc.message_id, mc.citation_index
            """
        ),
        {"user_id": str(user_id), "message_ids": [str(message.id) for message in messages]},
    )
    grouped: dict[UUID, list[CitationResponse]] = {}
    for row in result.mappings():
        message_id = row["message_id"]
        grouped.setdefault(message_id, []).append(
            CitationResponse.model_validate(
                {key: value for key, value in dict(row).items() if key != "message_id"}
            )
        )
    return grouped


async def _insert_message(
    session: AsyncSession,
    *,
    user_id: UUID,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    status: str,
    provider: str | None = None,
    model: str | None = None,
    error_code: str | None = None,
) -> UUID:
    result = await session.execute(
        text(
            """
            INSERT INTO messages (
              conversation_id, user_id, role, content, status, provider, model, error_code
            )
            VALUES (
              :conversation_id, :user_id, :role, :content, :status, :provider, :model, :error_code
            )
            RETURNING id
            """
        ),
        {
            "conversation_id": str(conversation_id),
            "user_id": str(user_id),
            "role": role,
            "content": content[:12000],
            "status": status,
            "provider": provider,
            "model": model,
            "error_code": error_code,
        },
    )
    return cast(UUID, result.scalar_one())


async def _insert_citations(
    session: AsyncSession, *, user_id: UUID, message_id: UUID, chunks: list[RetrievedChunk]
) -> list[CitationResponse]:
    citations: list[CitationResponse] = []
    seen: set[tuple[UUID, int]] = set()
    for chunk in chunks:
        key = (chunk.document_id, chunk.page_number)
        if key in seen:
            continue
        seen.add(key)
        citation = CitationResponse(
            citation_index=len(citations) + 1,
            document_id=chunk.document_id,
            document_name=chunk.document_name,
            page_number=chunk.page_number,
            excerpt=chunk.content[:700],
        )
        citations.append(citation)
        await session.execute(
            text(
                """
                INSERT INTO message_citations (
                  message_id, user_id, document_id, chunk_id, page_number, citation_index, excerpt
                )
                VALUES (
                  :message_id, :user_id, :document_id, :chunk_id, :page_number,
                  :citation_index, :excerpt
                )
                """
            ),
            {
                "message_id": str(message_id),
                "user_id": str(user_id),
                "document_id": str(chunk.document_id),
                "chunk_id": str(chunk.chunk_id),
                "page_number": chunk.page_number,
                "citation_index": citation.citation_index,
                "excerpt": citation.excerpt,
            },
        )
    return citations


async def _validate_document_filter(
    session: AsyncSession, *, user_id: UUID, document_ids: list[UUID]
) -> None:
    if not document_ids:
        return
    result = await session.execute(
        text(
            """
            SELECT count(*)
            FROM documents
            WHERE user_id = :user_id
              AND id = ANY(:document_ids)
              AND status = 'ready'
              AND deleted_at IS NULL
            """
        ),
        {
            "user_id": str(user_id),
            "document_ids": [str(document_id) for document_id in document_ids],
        },
    )
    if int(result.scalar_one()) != len(set(document_ids)):
        raise ValueError("document_not_found")


async def _usage_counts(session: AsyncSession, *, user_id: UUID) -> dict[str, int]:
    periods = usage_periods()
    result = await session.execute(
        text(
            """
            SELECT period_type, message_count
            FROM usage_counters
            WHERE user_id = :user_id
              AND (
                (period_type = 'daily' AND period_start = :daily_start)
                OR (period_type = 'monthly' AND period_start = :monthly_start)
              )
            """
        ),
        {
            "user_id": str(user_id),
            "daily_start": periods.daily_start,
            "monthly_start": periods.monthly_start,
        },
    )
    counts = {"daily": 0, "monthly": 0}
    for row in result.mappings():
        counts[str(row["period_type"])] = int(row["message_count"])
    return counts


async def _increment_usage_or_raise(
    session: AsyncSession, *, user_id: UUID, settings: Settings
) -> UsageResponse:
    counts = await _usage_counts(session, user_id=user_id)
    if counts["daily"] >= settings.ai_daily_message_limit:
        raise PermissionError("daily_ai_message_limit_reached")
    if counts["monthly"] >= settings.ai_monthly_message_limit:
        raise PermissionError("monthly_ai_message_limit_reached")
    periods = usage_periods()
    for period_type, period_start in (
        ("daily", periods.daily_start),
        ("monthly", periods.monthly_start),
    ):
        await session.execute(
            text(
                """
                INSERT INTO usage_counters (user_id, period_type, period_start, message_count)
                VALUES (:user_id, :period_type, :period_start, 1)
                ON CONFLICT (user_id, period_type, period_start)
                DO UPDATE SET message_count = usage_counters.message_count + 1,
                              updated_at = now()
                """
            ),
            {"user_id": str(user_id), "period_type": period_type, "period_start": period_start},
        )
    return _usage_response(
        daily_used=counts["daily"] + 1,
        monthly_used=counts["monthly"] + 1,
        settings=settings,
    )


def _usage_response(*, daily_used: int, monthly_used: int, settings: Settings) -> UsageResponse:
    return UsageResponse(
        daily=UsageBucket(
            used=daily_used,
            limit=settings.ai_daily_message_limit,
            remaining=max(settings.ai_daily_message_limit - daily_used, 0),
        ),
        monthly=UsageBucket(
            used=monthly_used,
            limit=settings.ai_monthly_message_limit,
            remaining=max(settings.ai_monthly_message_limit - monthly_used, 0),
        ),
    )
