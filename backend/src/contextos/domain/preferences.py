from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

GreetingMode = Literal["full", "minimized", "direct"]
MotionMode = Literal["system", "reduced"]
ThemeMode = Literal["dark", "system"]


class PreferencesResponse(BaseModel):
    user_id: UUID
    greeting_mode: GreetingMode
    motion_mode: MotionMode
    theme_mode: ThemeMode
    welcome_completed: bool


class PreferencesPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    greeting_mode: GreetingMode | None = None
    motion_mode: MotionMode | None = None
    theme_mode: ThemeMode | None = None
    welcome_completed: bool | None = None


async def ensure_preferences(session: AsyncSession, user_id: UUID) -> PreferencesResponse:
    await session.execute(
        text(
            """
            INSERT INTO user_preferences (user_id)
            VALUES (:user_id)
            ON CONFLICT (user_id) DO NOTHING
            """
        ),
        {"user_id": str(user_id)},
    )
    return await get_preferences(session, user_id)


async def get_preferences(session: AsyncSession, user_id: UUID) -> PreferencesResponse:
    result = await session.execute(
        text(
            """
            SELECT user_id, greeting_mode, motion_mode, theme_mode, welcome_completed
            FROM user_preferences
            WHERE user_id = :user_id
            """
        ),
        {"user_id": str(user_id)},
    )
    row = result.mappings().one()
    return PreferencesResponse.model_validate(dict(row))


async def update_preferences(
    session: AsyncSession,
    user_id: UUID,
    patch: PreferencesPatch,
) -> PreferencesResponse:
    current = await ensure_preferences(session, user_id)
    values = current.model_dump()
    for key, value in patch.model_dump(exclude_unset=True).items():
        if value is not None:
            values[key] = value

    await session.execute(
        text(
            """
            UPDATE user_preferences
            SET greeting_mode = :greeting_mode,
                motion_mode = :motion_mode,
                theme_mode = :theme_mode,
                welcome_completed = :welcome_completed,
                updated_at = :updated_at
            WHERE user_id = :user_id
            """
        ),
        {
            "user_id": str(user_id),
            "greeting_mode": values["greeting_mode"],
            "motion_mode": values["motion_mode"],
            "theme_mode": values["theme_mode"],
            "welcome_completed": values["welcome_completed"],
            "updated_at": datetime.now(UTC),
        },
    )
    return await get_preferences(session, user_id)
