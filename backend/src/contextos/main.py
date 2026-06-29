from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Protocol

from fastapi import FastAPI

from contextos.api.router import api_router
from contextos.core.config import Settings, get_settings
from contextos.core.logging import configure_logging
from contextos.core.request_id import RequestIdMiddleware
from contextos.infrastructure.database import DatabaseResource
from contextos.infrastructure.redis_client import RedisResource


class LifespanResource(Protocol):
    async def start(self) -> None: ...
    async def close(self) -> None: ...


type ResourceFactory = Callable[[Settings], LifespanResource]


def create_app(
    settings: Settings | None = None,
    database_resource_factory: ResourceFactory = DatabaseResource,
    redis_resource_factory: ResourceFactory = RedisResource,
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
    app.add_middleware(RequestIdMiddleware)
    app.include_router(api_router)
    return app


app = create_app()
