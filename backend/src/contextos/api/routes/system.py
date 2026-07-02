from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from contextos.core.config import Settings
from contextos.infrastructure.database import DatabaseResource
from contextos.infrastructure.redis_client import RedisResource

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    return {
        "status": "ok",
        "service": settings.application_name,
        "version": settings.application_version,
    }


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    settings: Settings = request.app.state.settings
    database: DatabaseResource = request.app.state.database
    redis: RedisResource = request.app.state.redis

    database_ok, redis_ok = await asyncio.gather(
        database.health_check(settings.readiness_timeout_seconds),
        redis.health_check(settings.readiness_timeout_seconds),
    )

    checks: dict[str, str] = {
        "database": "ok" if database_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
    }
    if not database_ok or not redis_ok:
        logger.error("readiness check failed checks=%s", checks)

    payload: dict[str, str | dict[str, str]] = {
        "status": "ready" if database_ok and redis_ok else "not_ready",
        "checks": checks,
    }
    status_code = (
        status.HTTP_200_OK if database_ok and redis_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(status_code=status_code, content=payload)
