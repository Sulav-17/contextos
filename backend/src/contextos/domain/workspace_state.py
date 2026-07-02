from __future__ import annotations

import re
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from contextos.core.config import Settings

if TYPE_CHECKING:
    from contextos.domain.chat import UsageResponse


QUESTION_NORMALIZER = re.compile(r"[^a-z0-9\s]")


def match_workspace_state_intent(question: str) -> str | None:
    normalized = _normalize(question)
    if not normalized:
        return None

    if _matches_any(
        normalized,
        "do i have any pdfs uploaded",
        "do i have any pdf uploaded",
        "do i have any documents uploaded",
        "do i have any documents",
        "have i uploaded any pdfs",
        "have i uploaded any documents",
    ):
        return "document_presence"
    if _matches_any(
        normalized,
        "how many documents do i have",
        "how many pdfs do i have",
        "how many files do i have",
        "how many documents are in my library",
    ):
        return "document_count"
    if _matches_any(
        normalized,
        "what files are in my library",
        "what documents are in my library",
        "list my files",
        "list my documents",
        "list my pdfs",
    ):
        return "document_list"
    if _matches_any(
        normalized,
        "how many conversations do i have",
        "how many chats do i have",
    ):
        return "conversation_count"
    if _matches_any(
        normalized,
        "do i have any saved memories",
        "do i have any memories",
    ):
        return "memory_presence"
    if _matches_any(
        normalized,
        "how many approved memories do i have",
        "how many suggested memories do i have",
        "how many disabled memories do i have",
        "how many approved suggested or disabled memories do i have",
        "how many approved suggested disabled memories do i have",
    ):
        return "memory_counts"
    if _matches_any(
        normalized,
        "what is my usage today",
        "what is my daily usage",
        "how much usage do i have today",
    ):
        return "daily_usage"
    if _matches_any(
        normalized,
        "what is my monthly usage",
        "what is my usage this month",
        "how much monthly usage do i have",
    ):
        return "monthly_usage"
    return None


async def answer_workspace_state_question(
    session: AsyncSession,
    *,
    user_id: UUID,
    question: str,
    settings: Settings,
) -> tuple[str, UsageResponse] | None:
    intent = match_workspace_state_intent(question)
    if intent is None:
        return None

    from contextos.domain.chat import usage_status

    usage = await usage_status(session, user_id=user_id, settings=settings)
    if intent == "document_presence":
        count = await _count_documents(session, user_id=user_id)
        answer = (
            "Yes, you have uploaded PDFs."
            if count > 0
            else "No, you have not uploaded any PDFs yet."
        )
        return answer, usage
    if intent == "document_count":
        count = await _count_documents(session, user_id=user_id)
        return f"You have {count} document{'s' if count != 1 else ''}.", usage
    if intent == "document_list":
        names = await _list_document_names(session, user_id=user_id)
        if not names:
            return "Your library is empty.", usage
        return "Your library contains: " + ", ".join(names) + ".", usage
    if intent == "conversation_count":
        count = await _count_conversations(session, user_id=user_id)
        return f"You have {count} conversation{'s' if count != 1 else ''}.", usage
    if intent == "memory_presence":
        count = await _count_memories(session, user_id=user_id, status="approved")
        answer = (
            "Yes, you have saved memories."
            if count > 0
            else "No, you do not have any saved memories yet."
        )
        return answer, usage
    if intent == "memory_counts":
        approved, suggested, disabled = await _memory_counts(session, user_id=user_id)
        return (
            "You have "
            f"{approved} approved, {suggested} suggested, and {disabled} disabled memories.",
            usage,
        )
    if intent == "daily_usage":
        return (
            f"Today you have used {usage.daily.used} of {usage.daily.limit}. "
            f"{usage.daily.remaining} remaining.",
            usage,
        )
    if intent == "monthly_usage":
        return (
            f"This month you have used {usage.monthly.used} of {usage.monthly.limit}. "
            f"{usage.monthly.remaining} remaining.",
            usage,
        )
    return None


def _normalize(question: str) -> str:
    return " ".join(QUESTION_NORMALIZER.sub(" ", question.casefold()).split())


def _matches_any(normalized: str, *phrases: str) -> bool:
    return any(normalized == phrase for phrase in phrases)


async def _count_documents(session: AsyncSession, *, user_id: UUID) -> int:
    result = await session.execute(
        text(
            """
            SELECT count(*)
            FROM documents
            WHERE user_id = :user_id
              AND deleted_at IS NULL
              AND status <> 'deleted'
            """
        ),
        {"user_id": str(user_id)},
    )
    return int(result.scalar_one())


async def _list_document_names(session: AsyncSession, *, user_id: UUID) -> list[str]:
    result = await session.execute(
        text(
            """
            SELECT original_filename
            FROM documents
            WHERE user_id = :user_id
              AND deleted_at IS NULL
              AND status <> 'deleted'
            ORDER BY updated_at DESC, id DESC
            LIMIT 10
            """
        ),
        {"user_id": str(user_id)},
    )
    return [str(row["original_filename"]) for row in result.mappings()]


async def _count_conversations(session: AsyncSession, *, user_id: UUID) -> int:
    result = await session.execute(
        text(
            """
            SELECT count(*)
            FROM conversations
            WHERE user_id = :user_id
              AND deleted_at IS NULL
            """
        ),
        {"user_id": str(user_id)},
    )
    return int(result.scalar_one())


async def _count_memories(session: AsyncSession, *, user_id: UUID, status: str) -> int:
    result = await session.execute(
        text(
            """
            SELECT count(*)
            FROM memories
            WHERE user_id = :user_id
              AND deleted_at IS NULL
              AND status = :status
            """
        ),
        {"user_id": str(user_id), "status": status},
    )
    return int(result.scalar_one())


async def _memory_counts(session: AsyncSession, *, user_id: UUID) -> tuple[int, int, int]:
    result = await session.execute(
        text(
            """
            SELECT
              count(*) FILTER (WHERE status = 'approved') AS approved,
              count(*) FILTER (WHERE status = 'suggested') AS suggested,
              count(*) FILTER (WHERE status = 'disabled') AS disabled
            FROM memories
            WHERE user_id = :user_id
              AND deleted_at IS NULL
            """
        ),
        {"user_id": str(user_id)},
    )
    row = result.mappings().one()
    return int(row["approved"]), int(row["suggested"]), int(row["disabled"])
