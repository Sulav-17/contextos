from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from contextos.api.dependencies import AuthContext, require_auth
from contextos.domain.dashboard import DashboardResponse, get_dashboard

router = APIRouter(tags=["dashboard"])
AUTH_CONTEXT = Depends(require_auth)


@router.get("/api/v1/dashboard", response_model=DashboardResponse)
async def dashboard_route(
    response: Response,
    context: AuthContext = AUTH_CONTEXT,
) -> DashboardResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await get_dashboard(context.session, user_id=context.user.id, settings=context.settings)
