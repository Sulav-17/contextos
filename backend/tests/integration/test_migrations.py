from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import command
from alembic.config import Config
from tests.support import ensure_test_database, required_test_database_url


def build_alembic_config() -> Config:
    ensure_test_database()
    database_url = required_test_database_url(
        "CONTEXTOS_TEST_MIGRATION_DATABASE_URL",
        "CONTEXTOS_MIGRATION_DATABASE_URL",
    )

    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[2] / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


async def vector_extension_exists(database_url: str) -> bool:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
            return bool(result.scalar_one())
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_migration_upgrade_downgrade_cycle() -> None:
    ensure_test_database()
    database_url = required_test_database_url(
        "CONTEXTOS_TEST_MIGRATION_DATABASE_URL",
        "CONTEXTOS_MIGRATION_DATABASE_URL",
    )

    config = build_alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "head")
    assert asyncio.run(vector_extension_exists(database_url)) is True

    command.downgrade(config, "base")
    assert asyncio.run(vector_extension_exists(database_url)) is False

    command.upgrade(config, "head")
    assert asyncio.run(vector_extension_exists(database_url)) is True
