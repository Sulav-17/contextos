from __future__ import annotations

import os

import sqlalchemy as sa

from alembic import op

revision = "0002_auth_tenant_isolation"
down_revision = "0001_enable_vector_extension"
branch_labels = None
depends_on = None


def _runtime_role() -> str | None:
    role = os.getenv("POSTGRES_APP_USER", "").strip()
    return role or None


def _grant(sql: str) -> None:
    role = _runtime_role()
    if role:
        op.execute(sa.text(sql.replace(":runtime_role", f'"{role}"')))


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE TYPE user_role AS ENUM ('user', 'admin')")
    op.execute("CREATE TYPE user_status AS ENUM ('invited', 'active', 'disabled')")
    op.execute("CREATE TYPE greeting_mode AS ENUM ('full', 'minimized', 'direct')")
    op.execute("CREATE TYPE motion_mode AS ENUM ('system', 'reduced')")
    op.execute("CREATE TYPE theme_mode AS ENUM ('dark', 'system')")
    op.execute(
        "CREATE TYPE invitation_status AS ENUM "
        "('pending', 'sent', 'accepted', 'failed', 'revoked', 'expired')"
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("memory_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_authenticated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("email = lower(email)", name="ck_users_email_normalized"),
        sa.CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),
        sa.CheckConstraint("status IN ('invited', 'active', 'disabled')", name="ck_users_status"),
    )
    op.create_index("ux_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_preferences",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "greeting_mode",
            sa.Text(),
            nullable=False,
            server_default="minimized",
        ),
        sa.Column(
            "motion_mode",
            sa.Text(),
            nullable=False,
            server_default="system",
        ),
        sa.Column(
            "theme_mode",
            sa.Text(),
            nullable=False,
            server_default="dark",
        ),
        sa.Column(
            "welcome_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "greeting_mode IN ('full', 'minimized', 'direct')",
            name="ck_user_preferences_greeting_mode",
        ),
        sa.CheckConstraint(
            "motion_mode IN ('system', 'reduced')",
            name="ck_user_preferences_motion_mode",
        ),
        sa.CheckConstraint(
            "theme_mode IN ('dark', 'system')", name="ck_user_preferences_theme_mode"
        ),
    )

    op.create_table(
        "invitations",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("requested_role", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "invited_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("provider_user_id", sa.Text(), nullable=True),
        sa.Column("safe_provider_error_code", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("email = lower(email)", name="ck_invitations_email_normalized"),
        sa.CheckConstraint("requested_role IN ('user', 'admin')", name="ck_invitations_role"),
        sa.CheckConstraint(
            "status IN ('pending', 'sent', 'accepted', 'failed', 'revoked', 'expired')",
            name="ck_invitations_status",
        ),
    )
    op.create_index(
        "ux_invitations_active_email",
        "invitations",
        ["email"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'sent')"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "actor_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_audit_events_actor_created", "audit_events", ["actor_id", "created_at"])

    for table in ("users", "user_preferences", "invitations", "audit_events"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY users_own_read ON users
        FOR SELECT USING (id::text = current_setting('request.jwt.claim.sub', true))
        """
    )
    op.execute(
        """
        CREATE POLICY users_admin_read ON users
        FOR SELECT USING (current_setting('app.actor_role', true) = 'admin')
        """
    )
    op.execute(
        """
        CREATE POLICY users_own_login_update ON users
        FOR UPDATE
        USING (id::text = current_setting('request.jwt.claim.sub', true))
        WITH CHECK (id::text = current_setting('request.jwt.claim.sub', true))
        """
    )
    op.execute(
        """
        CREATE POLICY users_admin_insert ON users
        FOR INSERT
        WITH CHECK (current_setting('app.actor_role', true) = 'admin')
        """
    )
    op.execute(
        """
        CREATE POLICY preferences_owner ON user_preferences
        USING (user_id::text = current_setting('request.jwt.claim.sub', true))
        WITH CHECK (user_id::text = current_setting('request.jwt.claim.sub', true))
        """
    )
    op.execute(
        """
        CREATE POLICY invitations_admin ON invitations
        USING (current_setting('app.actor_role', true) = 'admin')
        WITH CHECK (current_setting('app.actor_role', true) = 'admin')
        """
    )
    op.execute(
        """
        CREATE POLICY audit_admin ON audit_events
        USING (current_setting('app.actor_role', true) = 'admin')
        WITH CHECK (current_setting('app.actor_role', true) = 'admin')
        """
    )

    _grant("GRANT USAGE ON SCHEMA public TO :runtime_role")
    _grant("GRANT SELECT, INSERT ON users TO :runtime_role")
    _grant(
        "GRANT UPDATE (status, activated_at, last_authenticated_at, updated_at) "
        "ON users TO :runtime_role"
    )
    _grant("GRANT SELECT, INSERT, UPDATE ON user_preferences TO :runtime_role")
    _grant("GRANT SELECT, INSERT, UPDATE ON invitations TO :runtime_role")
    _grant("GRANT SELECT, INSERT ON audit_events TO :runtime_role")


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_index("ux_invitations_active_email", table_name="invitations")
    op.drop_table("invitations")
    op.drop_table("user_preferences")
    op.drop_index("ux_users_email", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS invitation_status")
    op.execute("DROP TYPE IF EXISTS theme_mode")
    op.execute("DROP TYPE IF EXISTS motion_mode")
    op.execute("DROP TYPE IF EXISTS greeting_mode")
    op.execute("DROP TYPE IF EXISTS user_status")
    op.execute("DROP TYPE IF EXISTS user_role")
