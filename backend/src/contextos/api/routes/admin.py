from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from contextos.api.dependencies import AuthContext, require_admin
from contextos.domain.invitations import (
    InvitationCreate,
    InvitationListResponse,
    InvitationProvider,
    InvitationResponse,
    create_invitation,
    list_invitations,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
ADMIN_CONTEXT = Depends(require_admin)


@router.get("/invitations")
async def read_invitations(
    request: Request,
    context: AuthContext = ADMIN_CONTEXT,
) -> InvitationListResponse:
    return await list_invitations(context.session, request.app.state.settings.beta_max_users)


@router.post("/invitations", status_code=201)
async def send_invitation(
    payload: InvitationCreate,
    request: Request,
    context: AuthContext = ADMIN_CONTEXT,
) -> InvitationResponse:
    provider: InvitationProvider = request.app.state.invitation_provider
    return await create_invitation(
        context.session,
        provider,
        request.app.state.settings,
        context.user.id,
        payload,
    )
