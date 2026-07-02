from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from urllib.parse import quote, unquote, urlparse, urlunparse

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE_NAME = "contextos_test"
LOCAL_DATABASE_NAME = "contextos_local"
SAFE_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


@dataclass(frozen=True, slots=True)
class ParsedDatabaseUrl:
    raw: str
    username: str
    password: str | None
    hostname: str
    port: int | None
    database: str


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.fail(f"{name} is required for PostgreSQL-backed tests.")
    return value


def configure_test_database_environment() -> None:
    runtime_url = os.environ.get("CONTEXTOS_TEST_DATABASE_URL", "").strip()
    migration_url = os.environ.get("CONTEXTOS_TEST_MIGRATION_DATABASE_URL", "").strip()
    if not runtime_url:
        runtime_url = _derive_local_test_database_url(
            "CONTEXTOS_DATABASE_URL",
            expected_source_database=LOCAL_DATABASE_NAME,
            target_database=TEST_DATABASE_NAME,
        )
        os.environ["CONTEXTOS_TEST_DATABASE_URL"] = runtime_url
    if not migration_url:
        migration_url = _derive_local_test_database_url(
            "CONTEXTOS_MIGRATION_DATABASE_URL",
            expected_source_database=LOCAL_DATABASE_NAME,
            target_database=TEST_DATABASE_NAME,
        )
        os.environ["CONTEXTOS_TEST_MIGRATION_DATABASE_URL"] = migration_url

    os.environ["CONTEXTOS_DATABASE_URL"] = _validate_test_database_url(
        "CONTEXTOS_TEST_DATABASE_URL", runtime_url
    )
    os.environ["CONTEXTOS_MIGRATION_DATABASE_URL"] = _validate_test_database_url(
        "CONTEXTOS_TEST_MIGRATION_DATABASE_URL", migration_url
    )
    runtime = parse_database_url(runtime_url)
    os.environ.setdefault("POSTGRES_APP_USER", runtime.username)


def required_test_database_url(name: str, fallback_name: str) -> str:
    candidate = os.environ.get(name, "").strip()
    if candidate:
        return _validate_test_database_url(name, candidate)
    fallback = required_env(fallback_name)
    return _validate_test_database_url(fallback_name, fallback)


def ensure_test_database() -> None:
    configure_test_database_environment()
    runtime = parse_database_url(required_test_database_url("CONTEXTOS_TEST_DATABASE_URL", ""))
    migration = parse_database_url(
        required_test_database_url("CONTEXTOS_TEST_MIGRATION_DATABASE_URL", "")
    )
    if runtime.database != migration.database:
        pytest.fail(
            "CONTEXTOS_TEST_DATABASE_URL and CONTEXTOS_TEST_MIGRATION_DATABASE_URL must target "
            "the same isolated test database so migrations and runtime tests use one schema."
        )
    if runtime.hostname != migration.hostname or runtime.port != migration.port:
        pytest.fail("Test runtime and migration database URLs must use the same host and port.")
    asyncio.run(_ensure_test_database_async(runtime=runtime, migration=migration))


def parse_database_url(value: str) -> ParsedDatabaseUrl:
    parsed = urlparse(value)
    if parsed.scheme != "postgresql+asyncpg":
        pytest.fail("Test database URLs must use postgresql+asyncpg.")
    if not parsed.username:
        pytest.fail("Test database URLs must include a username.")
    if not parsed.hostname:
        pytest.fail("Test database URLs must include a hostname.")
    database = parsed.path.lstrip("/")
    if not database:
        pytest.fail("Test database URLs must include a database name.")
    return ParsedDatabaseUrl(
        raw=value,
        username=unquote(parsed.username),
        password=unquote(parsed.password) if parsed.password else None,
        hostname=parsed.hostname,
        port=parsed.port,
        database=database,
    )


def _validate_test_database_url(name: str, value: str) -> str:
    database_name = parse_database_url(value).database
    if "test" not in database_name.casefold() and "ci" not in database_name.casefold():
        pytest.fail(
            f"{name} must point to an isolated test database. "
            f"Received {database_name!r}, which does not look like a test database."
        )
    return value


def _derive_local_test_database_url(
    env_name: str,
    *,
    expected_source_database: str,
    target_database: str,
) -> str:
    source = parse_database_url(required_env(env_name))
    if source.database != expected_source_database or source.hostname not in SAFE_LOCAL_HOSTS:
        pytest.fail(
            f"{env_name} points to {source.database!r} on {source.hostname!r}. "
            "Set CONTEXTOS_TEST_DATABASE_URL and CONTEXTOS_TEST_MIGRATION_DATABASE_URL "
            "explicitly, or use the local Docker database."
        )
    return replace_database_name(source.raw, target_database)


def replace_database_name(value: str, database_name: str) -> str:
    parsed = urlparse(value)
    return urlunparse(parsed._replace(path=f"/{quote(database_name)}"))


async def _ensure_test_database_async(
    *, runtime: ParsedDatabaseUrl, migration: ParsedDatabaseUrl
) -> None:
    maintenance_url = replace_database_name(migration.raw, "postgres")
    maintenance_engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        async with maintenance_engine.connect() as connection:
            role_exists = (
                await connection.execute(
                    text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
                    {"role": runtime.username},
                )
            ).scalar_one_or_none()
            if role_exists is None:
                if runtime.password is None:
                    pytest.fail(
                        "CONTEXTOS_TEST_DATABASE_URL must include a password when the runtime "
                        "test role needs to be created."
                    )
                await connection.execute(
                    text(
                        f"CREATE ROLE {quote_identifier(runtime.username)} LOGIN PASSWORD "
                        f"'{_sql_literal(runtime.password)}' NOSUPERUSER NOCREATEDB "
                        "NOCREATEROLE NOINHERIT"
                    )
                )

            database_exists = (
                await connection.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :database"),
                    {"database": runtime.database},
                )
            ).scalar_one_or_none()
            if database_exists is None:
                await connection.execute(
                    text(f"CREATE DATABASE {quote_identifier(runtime.database)}")
                )
            await connection.execute(
                text(
                    f"GRANT CONNECT ON DATABASE {quote_identifier(runtime.database)} "
                    f"TO {quote_identifier(runtime.username)}"
                )
            )
    finally:
        await maintenance_engine.dispose()


def _sql_literal(value: str) -> str:
    return value.replace("'", "''")


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'
