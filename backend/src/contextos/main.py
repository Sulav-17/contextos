from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Protocol

from fastapi import FastAPI, Request
from fastapi.responses import Response

from contextos.api.errors import ContextOSError, contextos_error_handler
from contextos.api.router import api_router
from contextos.auth.jwt import SupabaseJwtVerifier
from contextos.core.config import Settings, get_settings
from contextos.core.logging import configure_logging
from contextos.core.request_id import RequestIdMiddleware
from contextos.domain.invitations import DisabledInvitationProvider, SupabaseInvitationProvider
from contextos.infrastructure.database import DatabaseResource
from contextos.infrastructure.redis_client import RedisResource


class LifespanResource(Protocol):
    async def start(self) -> None: ...
    async def close(self) -> None: ...


type ResourceFactory = Callable[[Settings], LifespanResource]
SENSITIVE_API_PREFIX = "/api/v1/"
NO_STORE = "private, no-store"


def build_invitation_provider(settings: Settings) -> object:
    if settings.supabase_secret_key is None:
        return DisabledInvitationProvider()
    return SupabaseInvitationProvider(settings)


def create_app(
    settings: Settings | None = None,
    database_resource_factory: ResourceFactory = DatabaseResource,
    redis_resource_factory: ResourceFactory = RedisResource,
    auth_provider_factory: Callable[[Settings], object] = SupabaseJwtVerifier,
    invitation_provider_factory: Callable[[Settings], object] = build_invitation_provider,
) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(log_level=app_settings.log_level, log_format=app_settings.log_format)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = database_resource_factory(app_settings)
        redis = redis_resource_factory(app_settings)
        app.state.database = database
        app.state.redis = redis
        app.state.settings = app_settings
        app.state.auth_provider = auth_provider_factory(app_settings)
        app.state.invitation_provider = invitation_provider_factory(app_settings)
        await database.start()
        await redis.start()
        try:
            yield
        finally:
            await redis.close()
            await database.close()

    app = FastAPI(
        title=app_settings.application_name,
        version=app_settings.application_version,
        lifespan=lifespan,
    )
    app.state.settings = app_settings

    @app.middleware("http")
    async def no_store_sensitive_api(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        if request.url.path.startswith(SENSITIVE_API_PREFIX):
            response.headers.setdefault("Cache-Control", NO_STORE)
        return response

    app.add_middleware(RequestIdMiddleware)
    app.add_exception_handler(ContextOSError, contextos_error_handler)
    app.include_router(api_router)
    return app


app = create_app()
