from __future__ import annotations

import argparse
import asyncio
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from contextos.core.config import get_settings
from contextos.domain.users import normalize_email


async def bootstrap_admin(auth_user_id: UUID, email: str) -> str:
    settings = get_settings()
    database_url = (
        settings.migration_database_url.get_secret_value()
        if settings.migration_database_url is not None
        else settings.database_url.get_secret_value()
    )
    engine = create_async_engine(database_url, pool_pre_ping=True)
    normalized_email = normalize_email(email)
    try:
        async with engine.begin() as connection:
            existing = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT id, email
                            FROM users
                            WHERE role = 'admin'
                            ORDER BY created_at
                            LIMIT 1
                            """
                        )
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is not None and existing["id"] != auth_user_id:
                raise RuntimeError("A different administrator already exists.")

            await connection.execute(
                text(
                    """
                    INSERT INTO users (id, email, role, status, activated_at)
                    VALUES (:id, :email, 'admin', 'active', now())
                    ON CONFLICT (id) DO UPDATE
                    SET email = EXCLUDED.email,
                        role = 'admin',
                        status = 'active',
                        activated_at = COALESCE(users.activated_at, now()),
                        updated_at = now()
                    """
                ),
                {"id": str(auth_user_id), "email": normalized_email},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO user_preferences (user_id)
                    VALUES (:id)
                    ON CONFLICT (user_id) DO NOTHING
                    """
                ),
                {"id": str(auth_user_id)},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO audit_events (actor_id, event_type, metadata)
                    VALUES (:id, 'administrator_bootstrap', '{"method": "cli"}'::json)
                    """
                ),
                {"id": str(auth_user_id)},
            )
    finally:
        await engine.dispose()
    return "Administrator bootstrap complete."


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap the first ContextOS administrator.")
    parser.add_argument("--auth-user-id", required=True, type=UUID)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    print(asyncio.run(bootstrap_admin(args.auth_user_id, args.email)))


if __name__ == "__main__":
    main()
