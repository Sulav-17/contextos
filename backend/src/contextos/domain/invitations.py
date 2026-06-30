from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal, Protocol
from uuid import NAMESPACE_URL, UUID, uuid5

import httpx
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from contextos.api.errors import ContextOSError
from contextos.auth.errors import BETA_CAPACITY_REACHED, INVITATION_DUPLICATE, PROVIDER_UNAVAILABLE
from contextos.core.config import Settings
from contextos.domain.users import normalize_email

InvitationRole = Literal["user", "admin"]


class InvitationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    role: InvitationRole = "user"


class InvitationResponse(BaseModel):
    id: UUID
    email: str
    requested_role: InvitationRole
    status: str
    expires_at: datetime
    sent_at: datetime | None
    accepted_at: datetime | None


class InvitationListResponse(BaseModel):
    beta_max_users: int
    occupied_slots: int
    invitations: list[InvitationResponse]


@dataclass(frozen=True)
class SentInvitation:
    provider_user_id: UUID


class InvitationProviderError(Exception):
    def __init__(self, safe_code: str) -> None:
        self.safe_code = safe_code
        super().__init__(safe_code)


class InvitationProvider(Protocol):
    async def send_invitation(self, email: str, redirect_to: str) -> SentInvitation: ...


class SupabaseInvitationProvider:
    def __init__(self, settings: Settings) -> None:
        if settings.supabase_secret_key is None:
            raise RuntimeError("Supabase secret key is required for invitations.")
        self._endpoint = settings.supabase_url.rstrip("/") + "/auth/v1/invite"
        self._secret_key = settings.supabase_secret_key.get_secret_value()

    async def send_invitation(self, email: str, redirect_to: str) -> SentInvitation:
        headers = {
            "Authorization": f"Bearer {self._secret_key}",
            "apikey": self._secret_key,
            "Content-Type": "application/json",
        }
        payload = {"email": email, "data": {}, "redirect_to": redirect_to}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(self._endpoint, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise InvitationProviderError("timeout") from exc
        except httpx.HTTPError as exc:
            raise InvitationProviderError("unavailable") from exc
        if response.status_code >= 400:
            raise InvitationProviderError("provider_rejected")
        data = response.json()
        provider_user_id = data.get("id")
        if not isinstance(provider_user_id, str):
            raise InvitationProviderError("provider_missing_user")
        try:
            return SentInvitation(provider_user_id=UUID(provider_user_id))
        except ValueError as exc:
            raise InvitationProviderError("provider_invalid_user") from exc


class DisabledInvitationProvider:
    async def send_invitation(self, email: str, redirect_to: str) -> SentInvitation:
        raise InvitationProviderError("not_configured")


class FakeInvitationProvider:
    def __init__(self, fail_code: str | None = None) -> None:
        self.fail_code = fail_code
        self.sent: list[tuple[str, str]] = []

    async def send_invitation(self, email: str, redirect_to: str) -> SentInvitation:
        self.sent.append((email, redirect_to))
        if self.fail_code:
            raise InvitationProviderError(self.fail_code)
        return SentInvitation(provider_user_id=uuid5(NAMESPACE_URL, f"contextos-test:{email}"))


async def list_invitations(
    session: AsyncSession,
    beta_max_users: int,
) -> InvitationListResponse:
    occupied_slots = await count_occupied_slots(session)
    result = await session.execute(
        text(
            """
            SELECT id, email, requested_role, status, expires_at, sent_at, accepted_at
            FROM invitations
            ORDER BY created_at DESC
            """
        )
    )
    invitations = [InvitationResponse.model_validate(dict(row)) for row in result.mappings()]
    return InvitationListResponse(
        beta_max_users=beta_max_users,
        occupied_slots=occupied_slots,
        invitations=invitations,
    )


async def create_invitation(
    session: AsyncSession,
    provider: InvitationProvider,
    settings: Settings,
    actor_id: UUID,
    payload: InvitationCreate,
) -> InvitationResponse:
    email = normalize_email(payload.email)
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=7)
    await session.execute(text("SELECT pg_advisory_xact_lock(42004)"))

    if await count_occupied_slots(session) >= settings.beta_max_users:
        raise ContextOSError(BETA_CAPACITY_REACHED)
    if await active_invitation_exists(session, email):
        raise ContextOSError(INVITATION_DUPLICATE)
    if await user_exists(session, email):
        raise ContextOSError(INVITATION_DUPLICATE)

    invitation_id = (
        await session.execute(
            text(
                """
                INSERT INTO invitations (email, requested_role, status, invited_by, expires_at)
                VALUES (:email, :role, 'pending', :actor_id, :expires_at)
                RETURNING id
                """
            ),
            {
                "email": email,
                "role": payload.role,
                "actor_id": str(actor_id),
                "expires_at": expires_at,
            },
        )
    ).scalar_one()
    await record_audit(session, actor_id, "invitation_attempted", {"email": email})

    try:
        sent = await provider.send_invitation(
            email, settings.frontend_url.rstrip("/") + "/auth/confirm"
        )
    except InvitationProviderError as exc:
        await session.execute(
            text(
                """
                UPDATE invitations
                SET status = 'failed', safe_provider_error_code = :code, updated_at = :now
                WHERE id = :id
                """
            ),
            {"id": invitation_id, "code": exc.safe_code, "now": now},
        )
        await record_audit(
            session, actor_id, "invitation_failed", {"email": email, "code": exc.safe_code}
        )
        raise ContextOSError(PROVIDER_UNAVAILABLE) from exc

    await session.execute(
        text(
            """
            INSERT INTO users (id, email, role, status)
            VALUES (:user_id, :email, :role, 'invited')
            """
        ),
        {"user_id": str(sent.provider_user_id), "email": email, "role": payload.role},
    )
    await session.execute(
        text(
            """
            UPDATE invitations
            SET status = 'sent',
                provider_user_id = :provider_user_id,
                sent_at = :now,
                updated_at = :now
            WHERE id = :id
            """
        ),
        {"id": invitation_id, "provider_user_id": str(sent.provider_user_id), "now": now},
    )
    await record_audit(session, actor_id, "invitation_sent", {"email": email})
    return await get_invitation(session, invitation_id)


async def get_invitation(session: AsyncSession, invitation_id: UUID) -> InvitationResponse:
    result = await session.execute(
        text(
            """
            SELECT id, email, requested_role, status, expires_at, sent_at, accepted_at
            FROM invitations
            WHERE id = :id
            """
        ),
        {"id": invitation_id},
    )
    return InvitationResponse.model_validate(dict(result.mappings().one()))


async def count_occupied_slots(session: AsyncSession) -> int:
    result = await session.execute(
        text(
            """
            SELECT
              (SELECT count(*) FROM users WHERE status IN ('invited', 'active')) +
              (
                SELECT count(*)
                FROM invitations i
                WHERE i.status IN ('pending', 'sent')
                  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.email = i.email)
              )
            """
        )
    )
    return int(result.scalar_one())


async def active_invitation_exists(session: AsyncSession, email: str) -> bool:
    result = await session.execute(
        text(
            """
            SELECT EXISTS (
              SELECT 1
              FROM invitations
              WHERE email = :email AND status IN ('pending', 'sent')
            )
            """
        ),
        {"email": email},
    )
    return bool(result.scalar_one())


async def user_exists(session: AsyncSession, email: str) -> bool:
    result = await session.execute(
        text("SELECT EXISTS (SELECT 1 FROM users WHERE email = :email)"),
        {"email": email},
    )
    return bool(result.scalar_one())


async def record_audit(
    session: AsyncSession,
    actor_id: UUID | None,
    event_type: str,
    metadata: dict[str, str],
) -> None:
    await session.execute(
        text(
            """
            INSERT INTO audit_events (actor_id, event_type, metadata)
            VALUES (:actor_id, :event_type, :metadata)
            """
        ),
        {
            "actor_id": str(actor_id) if actor_id else None,
            "event_type": event_type,
            "metadata": metadata,
        },
    )
