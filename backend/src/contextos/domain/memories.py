from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Literal, cast
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from contextos.core.config import Settings
from contextos.domain.ai import build_embedding_provider

MemoryType = Literal[
    "identity",
    "background",
    "goal",
    "preference",
    "project",
    "decision",
    "constraint",
    "other",
]
MemoryStatus = Literal["suggested", "approved", "disabled", "rejected"]
SourceKind = Literal["manual", "conversation"]

MAX_MEMORY_CONTENT_LENGTH = 1200
MEMORY_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")
SECRET_PATTERNS = (
    re.compile(r"\b(password|passphrase|api key|apikey|token|secret|credential)\b", re.I),
    re.compile(r"\b[A-Za-z0-9_=-]{24,}\.[A-Za-z0-9_=-]{12,}\.[A-Za-z0-9_=-]{12,}\b"),
    re.compile(r"\b(sk|pk)_[A-Za-z0-9_]{16,}\b"),
)
SENSITIVE_PATTERNS = (
    re.compile(r"\b(religion|political|diagnosed|disability|sexuality|ethnicity)\b", re.I),
)
EXPLICIT_MEMORY_SAVE_PATTERNS: tuple[tuple[re.Pattern[str], MemoryType | None], ...] = (
    (re.compile(r"^remember that\b[\s:,-]*(?P<content>.*)$", re.I), None),
    (re.compile(r"^save this\b[\s:,-]*(?P<content>.*)$", re.I), None),
    (re.compile(r"^my goal is\b[\s:,-]*(?P<content>.*)$", re.I), "goal"),
    (re.compile(r"^i prefer\b[\s:,-]*(?P<content>.*)$", re.I), "preference"),
    (re.compile(r"^i decided\b[\s:,-]*(?P<content>.*)$", re.I), "decision"),
    (re.compile(r"^we decided\b[\s:,-]*(?P<content>.*)$", re.I), "decision"),
    (re.compile(r"^i am building\b[\s:,-]*(?P<content>.*)$", re.I), "project"),
    (re.compile(r"^my project is\b[\s:,-]*(?P<content>.*)$", re.I), "project"),
    (re.compile(r"^from now on\b[\s:,-]*(?P<content>.*)$", re.I), None),
)
QUESTION_PREFIX_PATTERN = re.compile(
    r"^(what|who|when|where|why|how|do|does|did|can|could|would|should|is|are|am|will|have|has)\b",
    re.I,
)
MEMORY_QUESTION_PATTERN = re.compile(
    r"\b("
    r"remember|memory|saved memory|goal|prefer|preference|preferred|decide|decision|"
    r"constraint|project|background|identity"
    r")\b",
    re.I,
)
QUESTION_STOPWORDS = {
    "what",
    "who",
    "when",
    "where",
    "why",
    "how",
    "do",
    "does",
    "did",
    "can",
    "could",
    "would",
    "should",
    "is",
    "are",
    "am",
    "will",
    "have",
    "has",
    "the",
    "a",
    "an",
    "my",
    "your",
    "you",
    "i",
    "we",
    "me",
    "it",
    "this",
    "that",
    "these",
    "those",
    "remember",
    "memory",
    "saved",
    "goal",
    "prefer",
    "preferred",
    "preference",
    "decide",
    "decided",
    "decision",
    "project",
    "background",
    "identity",
}
QUESTION_MEMORY_TYPE_HINTS: dict[MemoryType, tuple[str, ...]] = {
    "preference": ("prefer", "preferred", "preference"),
    "goal": ("goal", "want", "planning", "plan"),
    "decision": ("decide", "decided", "decision"),
    "project": ("project", "build", "building"),
    "constraint": ("constraint", "must", "never", "always", "only", "require"),
    "background": ("background", "about me", "who am i"),
    "identity": ("identity", "name", "who am i"),
}
BARE_MEMORY_TRIGGER_PHRASES = {"remember that", "save this"}


class MemoryCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_type: MemoryType
    content: str = Field(min_length=1, max_length=MAX_MEMORY_CONTENT_LENGTH)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        return validate_memory_content(value)


class MemoryUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_type: MemoryType | None = None
    content: str | None = Field(default=None, min_length=1, max_length=MAX_MEMORY_CONTENT_LENGTH)

    @field_validator("content")
    @classmethod
    def normalize_optional_content(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_memory_content(value)


class MemoryResponse(BaseModel):
    id: UUID
    memory_type: MemoryType
    content: str
    status: MemoryStatus
    source_kind: SourceKind
    source_conversation_id: UUID | None
    source_conversation_title: str | None = None
    source_message_id: UUID | None
    created_at: datetime
    updated_at: datetime
    disabled_at: datetime | None


class MemoryListResponse(BaseModel):
    memories: list[MemoryResponse]


class MemoryReference(BaseModel):
    id: UUID
    memory_type: MemoryType
    content: str
    source_conversation_id: UUID | None = None
    source_conversation_title: str | None = None


class RetrievedMemory(MemoryReference):
    distance: float

    @property
    def similarity(self) -> float:
        return 1.0 - self.distance


def normalize_memory_content(value: str) -> str:
    return " ".join(value.split()).strip()[:MAX_MEMORY_CONTENT_LENGTH]


def content_hash(content: str) -> str:
    return hashlib.sha256(normalize_memory_content(content).encode("utf-8")).hexdigest()


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


def contains_secret(content: str) -> bool:
    return any(pattern.search(content) for pattern in SECRET_PATTERNS)


def contains_unsupported_sensitive_inference(content: str) -> bool:
    lowered = content.casefold()
    if "remember" in lowered or "save" in lowered:
        return False
    return any(pattern.search(content) for pattern in SENSITIVE_PATTERNS)


def has_meaningful_memory_content(content: str) -> bool:
    words = MEMORY_WORD_PATTERN.findall(content)
    if not words:
        return False
    return any(len(word) >= 2 for word in words)


def validate_memory_content(value: str) -> str:
    normalized = normalize_memory_content(value)
    if not normalized:
        raise ValueError("content must not be blank")
    if normalized.casefold().rstrip("?.!,;:") in BARE_MEMORY_TRIGGER_PHRASES:
        raise ValueError("content must contain meaningful text")
    if not has_meaningful_memory_content(normalized):
        raise ValueError("content must contain meaningful text")
    if contains_secret(normalized):
        raise ValueError("content cannot contain secrets or credentials")
    return normalized


def is_valid_memory_content(value: str) -> bool:
    try:
        validate_memory_content(value)
    except ValueError:
        return False
    return True


def is_eligible_memory_content(value: str) -> bool:
    if not is_valid_memory_content(value):
        return False
    return not contains_unsupported_sensitive_inference(normalize_memory_content(value))


def infer_memory_type(content: str) -> MemoryType:
    lowered = content.casefold()
    if "i prefer" in lowered or "preferred" in lowered or "preference" in lowered:
        return "preference"
    if "my goal" in lowered or "i want to" in lowered or lowered.startswith("goal "):
        return "goal"
    if "i decided" in lowered or "we decided" in lowered:
        return "decision"
    if "i am building" in lowered or "my project" in lowered:
        return "project"
    if "from now on" in lowered:
        constraint_markers = ("must", "never", "always", "only", "constraint", "require")
        if any(marker in lowered for marker in constraint_markers):
            return "constraint"
        return "preference"
    return "other"


def is_memory_aware_question(question: str) -> bool:
    normalized = normalize_memory_content(question)
    if (
        not normalized
        or matches_explicit_memory_save_intent(normalized)
        or is_incomplete_memory_save_shell(normalized)
    ):
        return False
    is_question = normalized.endswith("?") or bool(QUESTION_PREFIX_PATTERN.match(normalized))
    return is_question and bool(MEMORY_QUESTION_PATTERN.search(normalized))


def matches_explicit_memory_save_intent(question: str) -> bool:
    return extract_memory_suggestion(question) is not None


def extract_memory_suggestion(question: str) -> tuple[MemoryType, str] | None:
    normalized = normalize_memory_content(question)
    for pattern, memory_type in EXPLICIT_MEMORY_SAVE_PATTERNS:
        match = pattern.match(normalized)
        if match is None:
            continue
        content = normalize_memory_content(match.group("content"))
        if not is_valid_memory_content(content):
            return None
        inferred_type = memory_type or infer_memory_type(normalized)
        if not is_eligible_memory_content(content):
            return None
        return inferred_type, content
    return None


def is_incomplete_memory_save_shell(question: str) -> bool:
    normalized = normalize_memory_content(question)
    for pattern, _ in EXPLICIT_MEMORY_SAVE_PATTERNS:
        match = pattern.match(normalized)
        if match is None:
            continue
        content = normalize_memory_content(match.group("content"))
        return not is_valid_memory_content(content)
    return False


async def create_manual_memory(
    session: AsyncSession, *, user_id: UUID, request: MemoryCreateRequest, settings: Settings
) -> MemoryResponse:
    memory = await _insert_memory(
        session,
        user_id=user_id,
        memory_type=request.memory_type,
        content=request.content,
        status="approved",
        source_kind="manual",
        source_conversation_id=None,
        source_message_id=None,
    )
    if memory is None:
        raise ValueError("memory_duplicate")
    await upsert_memory_embedding(
        session, user_id=user_id, memory_id=memory.id, settings=settings
    )
    return memory


async def list_memories(
    session: AsyncSession, *, user_id: UUID, status: MemoryStatus | None = None
) -> MemoryListResponse:
    params: dict[str, object] = {"user_id": str(user_id)}
    status_sql = ""
    if status is not None:
        status_sql = "AND status = :status"
        params["status"] = status
    result = await session.execute(
        text(
            f"""
            SELECT m.id, m.memory_type, m.content, m.status, m.source_kind,
                   m.source_conversation_id, c.title AS source_conversation_title,
                   m.source_message_id, m.created_at, m.updated_at, m.disabled_at
            FROM memories m
            LEFT JOIN conversations c
              ON c.id = m.source_conversation_id
             AND c.user_id = m.user_id
             AND c.deleted_at IS NULL
            WHERE m.user_id = :user_id
              AND m.deleted_at IS NULL
              {status_sql}
            ORDER BY m.updated_at DESC, m.id DESC
            """
        ),
        params,
    )
    return MemoryListResponse(
        memories=[MemoryResponse.model_validate(dict(row)) for row in result.mappings()]
    )


async def create_memory_suggestion_from_message(
    session: AsyncSession,
    *,
    user_id: UUID,
    conversation_id: UUID,
    message_id: UUID,
    content: str,
) -> MemoryResponse | None:
    extracted = extract_memory_suggestion(content)
    if extracted is None:
        return None
    memory_type, memory_content = extracted
    return await _insert_memory(
        session,
        user_id=user_id,
        memory_type=memory_type,
        content=memory_content,
        status="suggested",
        source_kind="conversation",
        source_conversation_id=conversation_id,
        source_message_id=message_id,
        allow_duplicate=True,
    )


async def update_memory(
    session: AsyncSession,
    *,
    user_id: UUID,
    memory_id: UUID,
    request: MemoryUpdateRequest,
    settings: Settings,
) -> MemoryResponse | None:
    existing = await get_memory(session, user_id=user_id, memory_id=memory_id)
    if existing is None or existing.status == "rejected":
        return None
    new_type = request.memory_type or existing.memory_type
    new_content = request.content or existing.content
    result = await session.execute(
        text(
            """
            UPDATE memories
            SET memory_type = :memory_type,
                content = :content,
                content_sha256 = :content_sha256,
                updated_at = :now
            WHERE id = :memory_id AND user_id = :user_id AND deleted_at IS NULL
            RETURNING id, memory_type, content, status, source_kind, source_conversation_id,
                      NULL::text AS source_conversation_title,
                      source_message_id, created_at, updated_at, disabled_at
            """
        ),
        {
            "memory_id": str(memory_id),
            "user_id": str(user_id),
            "memory_type": new_type,
            "content": new_content,
            "content_sha256": content_hash(new_content),
            "now": datetime.now(UTC),
        },
    )
    row = result.mappings().one_or_none()
    if row is None:
        return None
    memory = MemoryResponse.model_validate(dict(row))
    await session.execute(
        text("DELETE FROM memory_embeddings WHERE memory_id = :memory_id AND user_id = :user_id"),
        {"memory_id": str(memory_id), "user_id": str(user_id)},
    )
    if memory.status == "approved":
        await upsert_memory_embedding(
            session, user_id=user_id, memory_id=memory_id, settings=settings
        )
    return memory


async def approve_memory(
    session: AsyncSession, *, user_id: UUID, memory_id: UUID, settings: Settings
) -> MemoryResponse | None:
    existing = await get_memory(session, user_id=user_id, memory_id=memory_id)
    if existing is None or not is_eligible_memory_content(existing.content):
        return None
    memory = await _set_memory_status(
        session, user_id=user_id, memory_id=memory_id, status="approved", disabled_at=None
    )
    if memory is not None:
        await upsert_memory_embedding(
            session, user_id=user_id, memory_id=memory_id, settings=settings
        )
    return memory


async def reject_memory(
    session: AsyncSession, *, user_id: UUID, memory_id: UUID
) -> MemoryResponse | None:
    memory = await _set_memory_status(
        session, user_id=user_id, memory_id=memory_id, status="rejected", disabled_at=None
    )
    if memory is not None:
        await delete_memory_embedding(session, user_id=user_id, memory_id=memory_id)
    return memory


async def disable_memory(
    session: AsyncSession, *, user_id: UUID, memory_id: UUID
) -> MemoryResponse | None:
    memory = await _set_memory_status(
        session,
        user_id=user_id,
        memory_id=memory_id,
        status="disabled",
        disabled_at=datetime.now(UTC),
    )
    if memory is not None:
        await delete_memory_embedding(session, user_id=user_id, memory_id=memory_id)
    return memory


async def enable_memory(
    session: AsyncSession, *, user_id: UUID, memory_id: UUID, settings: Settings
) -> MemoryResponse | None:
    existing = await get_memory(session, user_id=user_id, memory_id=memory_id)
    if existing is None or not is_eligible_memory_content(existing.content):
        return None
    memory = await _set_memory_status(
        session, user_id=user_id, memory_id=memory_id, status="approved", disabled_at=None
    )
    if memory is not None:
        await upsert_memory_embedding(
            session, user_id=user_id, memory_id=memory_id, settings=settings
        )
    return memory


async def delete_memory(session: AsyncSession, *, user_id: UUID, memory_id: UUID) -> bool:
    result = await session.execute(
        text(
            """
            UPDATE memories
            SET deleted_at = :now, updated_at = :now
            WHERE id = :memory_id AND user_id = :user_id AND deleted_at IS NULL
            """
        ),
        {"memory_id": str(memory_id), "user_id": str(user_id), "now": datetime.now(UTC)},
    )
    await delete_memory_embedding(session, user_id=user_id, memory_id=memory_id)
    return cast(CursorResult[object], result).rowcount == 1


async def get_memory(
    session: AsyncSession, *, user_id: UUID, memory_id: UUID
) -> MemoryResponse | None:
    result = await session.execute(
        text(
            """
            SELECT m.id, m.memory_type, m.content, m.status, m.source_kind,
                   m.source_conversation_id, c.title AS source_conversation_title,
                   m.source_message_id, m.created_at, m.updated_at, m.disabled_at
            FROM memories m
            LEFT JOIN conversations c
              ON c.id = m.source_conversation_id
             AND c.user_id = m.user_id
             AND c.deleted_at IS NULL
            WHERE m.id = :memory_id AND m.user_id = :user_id AND m.deleted_at IS NULL
            """
        ),
        {"memory_id": str(memory_id), "user_id": str(user_id)},
    )
    row = result.mappings().one_or_none()
    return MemoryResponse.model_validate(dict(row)) if row is not None else None


async def retrieve_memories(
    session: AsyncSession, *, user_id: UUID, query_embedding: list[float], settings: Settings
) -> list[RetrievedMemory]:
    result = await session.execute(
        text(
            """
            SELECT m.id, m.memory_type, m.content, m.source_conversation_id,
                   c.title AS source_conversation_title,
                   me.embedding <=> CAST(:embedding AS vector) AS distance
            FROM memories m
            JOIN memory_embeddings me ON me.memory_id = m.id AND me.user_id = m.user_id
            LEFT JOIN conversations c
              ON c.id = m.source_conversation_id
             AND c.user_id = m.user_id
             AND c.deleted_at IS NULL
            WHERE m.user_id = :user_id
              AND m.status = 'approved'
              AND m.deleted_at IS NULL
              AND me.embedding_provider = :provider
              AND me.embedding_model = :model
              AND me.embedding_dimension = :dimension
              AND me.content_sha256 = m.content_sha256
              AND 1 - (me.embedding <=> CAST(:embedding AS vector)) >= :threshold
            ORDER BY me.embedding <=> CAST(:embedding AS vector), m.updated_at DESC
            LIMIT :limit
            """
        ),
        {
            "user_id": str(user_id),
            "embedding": vector_literal(query_embedding),
            "provider": settings.embedding_provider,
            "model": settings.embedding_model,
            "dimension": settings.embedding_dimension,
            "threshold": settings.memory_retrieval_similarity_threshold,
            "limit": settings.memory_retrieval_top_k,
        },
    )
    memories = [
        RetrievedMemory.model_validate(dict(row))
        for row in result.mappings()
        if is_eligible_memory_content(str(row["content"]))
    ]
    bounded: list[RetrievedMemory] = []
    seen_hashes: set[str] = set()
    remaining = settings.memory_retrieval_max_context_characters
    for memory in memories:
        key = content_hash(memory.content)
        if key in seen_hashes:
            continue
        seen_hashes.add(key)
        content = memory.content[:remaining]
        if not content:
            break
        bounded.append(memory.model_copy(update={"content": content}))
        remaining -= len(content)
    return bounded


async def retrieve_memories_for_question(
    session: AsyncSession,
    *,
    user_id: UUID,
    question: str,
    query_embedding: list[float],
    settings: Settings,
) -> list[RetrievedMemory]:
    semantic = await retrieve_memories(
        session, user_id=user_id, query_embedding=query_embedding, settings=settings
    )
    question_types = _question_memory_types(question)
    question_tokens = _question_tokens(question)
    semantic = [
        memory
        for memory in semantic
        if _memory_question_score(
            memory,
            question_types=question_types,
            question_tokens=question_tokens,
        )
        > 0
    ]
    lexical = await _retrieve_memory_question_candidates(
        session, user_id=user_id, question=question, settings=settings
    )
    combined: list[RetrievedMemory] = []
    seen_ids: set[UUID] = set()
    for memory in semantic + lexical:
        if memory.id in seen_ids:
            continue
        seen_ids.add(memory.id)
        combined.append(memory)
    return _bound_memory_context(combined, settings)


async def _retrieve_memory_question_candidates(
    session: AsyncSession,
    *,
    user_id: UUID,
    question: str,
    settings: Settings,
) -> list[RetrievedMemory]:
    result = await session.execute(
        text(
            """
            SELECT m.id, m.memory_type, m.content, m.source_conversation_id,
                   c.title AS source_conversation_title, m.updated_at
            FROM memories m
            LEFT JOIN conversations c
              ON c.id = m.source_conversation_id
             AND c.user_id = m.user_id
             AND c.deleted_at IS NULL
            WHERE m.user_id = :user_id
              AND m.status = 'approved'
              AND m.deleted_at IS NULL
            ORDER BY m.updated_at DESC, m.id DESC
            LIMIT :scan_limit
            """
        ),
        {
            "user_id": str(user_id),
            "scan_limit": max(settings.memory_retrieval_top_k * 8, settings.memory_retrieval_top_k),
        },
    )
    question_types = _question_memory_types(question)
    question_tokens = _question_tokens(question)
    scored: list[tuple[int, datetime, RetrievedMemory]] = []
    for row in result.mappings():
        content = str(row["content"])
        if not is_eligible_memory_content(content):
            continue
        memory = RetrievedMemory.model_validate(
            {
                "id": row["id"],
                "memory_type": row["memory_type"],
                "content": content,
                "source_conversation_id": row["source_conversation_id"],
                "source_conversation_title": row["source_conversation_title"],
                "distance": 0.0,
            }
        )
        score = _memory_question_score(
            memory,
            question_types=question_types,
            question_tokens=question_tokens,
        )
        if score <= 0:
            continue
        scored.append((score, row["updated_at"], memory))
    scored.sort(key=lambda item: (-item[0], -item[1].timestamp(), item[2].id))
    return [memory for _, _, memory in scored[: settings.memory_retrieval_top_k]]


def _question_tokens(question: str) -> set[str]:
    return {
        token
        for token in MEMORY_WORD_PATTERN.findall(question.casefold())
        if token not in QUESTION_STOPWORDS and len(token) >= 3
    }


def _question_memory_types(question: str) -> set[MemoryType]:
    lowered = normalize_memory_content(question).casefold()
    question_types: set[MemoryType] = set()
    for memory_type, markers in QUESTION_MEMORY_TYPE_HINTS.items():
        if any(marker in lowered for marker in markers):
            question_types.add(memory_type)
    return question_types


def _memory_question_score(
    memory: RetrievedMemory,
    *,
    question_types: set[MemoryType],
    question_tokens: set[str],
) -> int:
    memory_tokens = {
        token
        for token in MEMORY_WORD_PATTERN.findall(memory.content.casefold())
        if token not in QUESTION_STOPWORDS and len(token) >= 3
    }
    overlap = len(question_tokens & memory_tokens)
    type_score = 4 if memory.memory_type in question_types else 0
    if overlap == 0 and type_score == 0:
        return 0
    return type_score + overlap


def _bound_memory_context(
    memories: list[RetrievedMemory], settings: Settings
) -> list[RetrievedMemory]:
    bounded: list[RetrievedMemory] = []
    seen_hashes: set[str] = set()
    remaining = settings.memory_retrieval_max_context_characters
    for memory in memories:
        key = content_hash(memory.content)
        if key in seen_hashes:
            continue
        seen_hashes.add(key)
        content = memory.content[:remaining]
        if not content:
            break
        bounded.append(memory.model_copy(update={"content": content}))
        remaining -= len(content)
    return bounded


async def upsert_memory_embedding(
    session: AsyncSession, *, user_id: UUID, memory_id: UUID, settings: Settings
) -> None:
    memory = await get_memory(session, user_id=user_id, memory_id=memory_id)
    if memory is None or memory.status != "approved":
        return
    provider = build_embedding_provider(settings)
    embedding = (await provider.embed([memory.content]))[0]
    await session.execute(
        text(
            """
            INSERT INTO memory_embeddings (
              memory_id, user_id, embedding, embedding_provider, embedding_model,
              embedding_dimension, content_sha256, embedding_created_at
            )
            VALUES (
              :memory_id, :user_id, CAST(:embedding AS vector), :provider, :model,
              :dimension, :content_sha256, :now
            )
            ON CONFLICT (memory_id) DO UPDATE
            SET embedding = EXCLUDED.embedding,
                embedding_provider = EXCLUDED.embedding_provider,
                embedding_model = EXCLUDED.embedding_model,
                embedding_dimension = EXCLUDED.embedding_dimension,
                content_sha256 = EXCLUDED.content_sha256,
                embedding_created_at = EXCLUDED.embedding_created_at
            """
        ),
        {
            "memory_id": str(memory_id),
            "user_id": str(user_id),
            "embedding": vector_literal(embedding),
            "provider": provider.provider,
            "model": provider.model,
            "dimension": provider.dimension,
            "content_sha256": content_hash(memory.content),
            "now": datetime.now(UTC),
        },
    )


async def delete_memory_embedding(session: AsyncSession, *, user_id: UUID, memory_id: UUID) -> None:
    await session.execute(
        text("DELETE FROM memory_embeddings WHERE memory_id = :memory_id AND user_id = :user_id"),
        {"memory_id": str(memory_id), "user_id": str(user_id)},
    )


async def _insert_memory(
    session: AsyncSession,
    *,
    user_id: UUID,
    memory_type: MemoryType,
    content: str,
    status: MemoryStatus,
    source_kind: SourceKind,
    source_conversation_id: UUID | None,
    source_message_id: UUID | None,
    allow_duplicate: bool = False,
) -> MemoryResponse | None:
    normalized = validate_memory_content(content)
    conflict_sql = (
        "ON CONFLICT ON CONSTRAINT ux_memories_user_content DO NOTHING"
        if allow_duplicate
        else ""
    )
    result = await session.execute(
        text(
            f"""
            INSERT INTO memories (
              user_id, memory_type, content, status, source_kind, source_conversation_id,
              source_message_id, content_sha256, disabled_at
            )
            VALUES (
              :user_id, :memory_type, :content, :status, :source_kind,
              :source_conversation_id, :source_message_id, :content_sha256, :disabled_at
            )
            {conflict_sql}
            RETURNING id, memory_type, content, status, source_kind, source_conversation_id,
                      NULL::text AS source_conversation_title,
                      source_message_id, created_at, updated_at, disabled_at
            """
        ),
        {
            "user_id": str(user_id),
            "memory_type": memory_type,
            "content": normalized,
            "status": status,
            "source_kind": source_kind,
            "source_conversation_id": (
                str(source_conversation_id) if source_conversation_id else None
            ),
            "source_message_id": str(source_message_id) if source_message_id else None,
            "content_sha256": content_hash(normalized),
            "disabled_at": datetime.now(UTC) if status == "disabled" else None,
        },
    )
    row = result.mappings().one_or_none()
    if row is not None:
        return MemoryResponse.model_validate(dict(row))
    duplicate = await session.execute(
        text(
            """
            SELECT m.id, m.memory_type, m.content, m.status, m.source_kind,
                   m.source_conversation_id, c.title AS source_conversation_title,
                   m.source_message_id, m.created_at, m.updated_at, m.disabled_at
            FROM memories m
            LEFT JOIN conversations c
              ON c.id = m.source_conversation_id
             AND c.user_id = m.user_id
             AND c.deleted_at IS NULL
            WHERE m.user_id = :user_id
              AND m.content_sha256 = :content_sha256
              AND m.deleted_at IS NULL
            ORDER BY m.updated_at DESC
            LIMIT 1
            """
        ),
        {"user_id": str(user_id), "content_sha256": content_hash(normalized)},
    )
    duplicate_row = duplicate.mappings().one_or_none()
    return MemoryResponse.model_validate(dict(duplicate_row)) if duplicate_row is not None else None


async def _set_memory_status(
    session: AsyncSession,
    *,
    user_id: UUID,
    memory_id: UUID,
    status: MemoryStatus,
    disabled_at: datetime | None,
) -> MemoryResponse | None:
    result = await session.execute(
        text(
            """
            UPDATE memories
            SET status = :status,
                disabled_at = :disabled_at,
                updated_at = :now
            WHERE id = :memory_id AND user_id = :user_id AND deleted_at IS NULL
            RETURNING id, memory_type, content, status, source_kind, source_conversation_id,
                      NULL::text AS source_conversation_title,
                      source_message_id, created_at, updated_at, disabled_at
            """
        ),
        {
            "memory_id": str(memory_id),
            "user_id": str(user_id),
            "status": status,
            "disabled_at": disabled_at,
            "now": datetime.now(UTC),
        },
    )
    row = result.mappings().one_or_none()
    return MemoryResponse.model_validate(dict(row)) if row is not None else None
