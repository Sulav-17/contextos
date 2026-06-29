from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from contextos.core.config import Settings


class DatabaseResource:
    def __init__(self, settings: Settings) -> None:
        self._database_url = settings.database_url.get_secret_value()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def start(self) -> None:
        if self._engine is not None:
            return

        self._engine = create_async_engine(self._database_url, pool_pre_ping=True)
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    async def health_check(self, timeout_seconds: float) -> bool:
        engine = self._engine
        if engine is None:
            return False

        async def run_query() -> bool:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return True

        try:
            return await asyncio.wait_for(run_query(), timeout=timeout_seconds)
        except (TimeoutError, OSError):
            return False
        except Exception:
            return False

    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Database resource has not been started.")
        async with self._session_factory() as session:
            yield session
