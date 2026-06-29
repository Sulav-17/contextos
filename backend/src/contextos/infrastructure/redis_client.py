from __future__ import annotations

import asyncio

from redis.asyncio import Redis

from contextos.core.config import Settings


class RedisResource:
    def __init__(self, settings: Settings) -> None:
        self._redis_url = settings.redis_url.get_secret_value()
        self._client: Redis | None = None

    async def start(self) -> None:
        if self._client is not None:
            return
        self._client = Redis.from_url(self._redis_url, decode_responses=True)

    async def close(self) -> None:
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None

    async def health_check(self, timeout_seconds: float) -> bool:
        client = self._client
        if client is None:
            return False
        try:
            return await asyncio.wait_for(client.ping(), timeout=timeout_seconds)
        except (TimeoutError, OSError):
            return False
        except Exception:
            return False
