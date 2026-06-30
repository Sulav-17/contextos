from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from contextos.api.errors import ContextOSError
from contextos.auth.errors import (
    ACCOUNT_DISABLED,
    ADMINISTRATOR_REQUIRED,
    AUTHENTICATION_REQUIRED,
    INVALID_AUTHENTICATION,
)
from contextos.auth.jwt import AuthenticationError, AuthProvider
from contextos.auth.principal import ApplicationUser, Principal
from contextos.core.config import Settings
from contextos.domain.users import (
    activate_invited_user,
    get_application_user,
    provision_application_user,
    record_login,
)
from contextos.infrastructure.database import DatabaseResource
from contextos.infrastructure.tenant_context import set_tenant_context


@dataclass(slots=True)
class AuthContext:
    session: AsyncSession
    principal: Principal
    user: ApplicationUser
    settings: Settings


async def authenticated_context(request: Request) -> AsyncIterator[AuthContext]:
    authorization = request.headers.get("Authorization")
    provider: AuthProvider = request.app.state.auth_provider
    try:
        principal = await provider.verify_authorization_header(authorization)
    except AuthenticationError as exc:
        if exc.code == AUTHENTICATION_REQUIRED.code:
            raise ContextOSError(AUTHENTICATION_REQUIRED) from exc
        raise ContextOSError(INVALID_AUTHENTICATION) from exc

    database: DatabaseResource = request.app.state.database
    async for session in database.session():
        async with session.begin():
            await set_tenant_context(session, principal.subject, "user")
            user = await get_application_user(session, principal.subject)
            if user is None:
                if principal.email is None:
                    raise ContextOSError(INVALID_AUTHENTICATION)
                await set_tenant_context(session, principal.subject, "admin")
                user = await provision_application_user(
                    session,
                    principal.subject,
                    principal.email,
                )
            if user.status == "disabled":
                raise ContextOSError(ACCOUNT_DISABLED)
            if user.status == "invited":
                user = await activate_invited_user(session, principal.subject) or user
            await set_tenant_context(session, principal.subject, user.role)
            await record_login(session, principal.subject)
            yield AuthContext(
                session=session,
                principal=principal,
                user=user,
                settings=request.app.state.settings,
            )


AUTHENTICATED_CONTEXT = Depends(authenticated_context)


async def require_auth(
    context: AuthContext = AUTHENTICATED_CONTEXT,
) -> AuthContext:
    return context


async def require_admin(
    context: AuthContext = AUTHENTICATED_CONTEXT,
) -> AuthContext:
    if not context.user.is_admin:
        raise ContextOSError(ADMINISTRATOR_REQUIRED)
    return context
