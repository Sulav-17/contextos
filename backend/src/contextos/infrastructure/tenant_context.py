from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_tenant_context(session: AsyncSession, actor_id: UUID, actor_role: str) -> None:
    await session.execute(
        text("SELECT set_config('request.jwt.claim.sub', :actor_id, true)"),
        {"actor_id": str(actor_id)},
    )
    await session.execute(
        text("SELECT set_config('app.actor_role', :actor_role, true)"),
        {"actor_role": actor_role},
    )
