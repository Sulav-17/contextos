from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel

from contextos.api.dependencies import AuthContext, require_auth
from contextos.domain.preferences import (
    PreferencesPatch,
    PreferencesResponse,
    ensure_preferences,
    update_preferences,
)

router = APIRouter(prefix="/api/v1/me", tags=["me"])
AUTH_CONTEXT = Depends(require_auth)
NO_STORE_HEADERS = {"Cache-Control": "private, no-store"}


class MeResponse(BaseModel):
    id: str
    email: str
    display_name: str | None
    role: str
    status: str
    memory_enabled: bool


@router.get("")
async def read_me(
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> MeResponse:
    response.headers["Cache-Control"] = NO_STORE_HEADERS["Cache-Control"]
    user = context.user
    await ensure_preferences(context.session, user.id)
    return MeResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        status=user.status,
        memory_enabled=user.memory_enabled,
    )


@router.get("/preferences")
async def read_preferences(
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> PreferencesResponse:
    response.headers["Cache-Control"] = NO_STORE_HEADERS["Cache-Control"]
    return await ensure_preferences(context.session, context.user.id)


@router.patch("/preferences")
async def patch_preferences(
    payload: PreferencesPatch,
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> PreferencesResponse:
    response.headers["Cache-Control"] = NO_STORE_HEADERS["Cache-Control"]
    return await update_preferences(context.session, context.user.id, payload)
