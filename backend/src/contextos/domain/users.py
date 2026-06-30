from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from contextos.auth.principal import ApplicationUser


def normalize_email(email: str) -> str:
    return email.strip().casefold()


async def get_application_user(session: AsyncSession, user_id: UUID) -> ApplicationUser | None:
    result = await session.execute(
        text(
            """
            SELECT id, email, display_name, role, status, memory_enabled
            FROM users
            WHERE id = :user_id
            """
        ),
        {"user_id": str(user_id)},
    )
    row = result.mappings().one_or_none()
    if row is None:
        return None
    return ApplicationUser(
        id=row["id"],
        email=row["email"],
        display_name=row["display_name"],
        role=row["role"],
        status=row["status"],
        memory_enabled=row["memory_enabled"],
    )


async def activate_invited_user(session: AsyncSession, user_id: UUID) -> ApplicationUser | None:
    now = datetime.now(UTC)
    await session.execute(
        text(
            """
            UPDATE users
            SET status = 'active',
                activated_at = COALESCE(activated_at, :now),
                last_authenticated_at = :now,
                updated_at = :now
            WHERE id = :user_id AND status = 'invited'
            """
        ),
        {"user_id": str(user_id), "now": now},
    )
    return await get_application_user(session, user_id)


async def provision_application_user(
    session: AsyncSession,
    user_id: UUID,
    email: str,
) -> ApplicationUser:
    normalized_email = normalize_email(email)
    now = datetime.now(UTC)
    await session.execute(
        text(
            """
            INSERT INTO users (id, email, role, status, activated_at, created_at, updated_at)
            VALUES (:user_id, :email, 'user', 'active', :now, :now, :now)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {"user_id": str(user_id), "email": normalized_email, "now": now},
    )
    user = await get_application_user(session, user_id)
    if user is None:
        raise RuntimeError("application user provisioning did not create a resolvable user")
    return user


async def record_login(session: AsyncSession, user_id: UUID) -> None:
    await session.execute(
        text("UPDATE users SET last_authenticated_at = :now WHERE id = :user_id"),
        {"user_id": str(user_id), "now": datetime.now(UTC)},
    )
