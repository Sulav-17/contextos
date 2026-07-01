from __future__ import annotations

import os

import sqlalchemy as sa

from alembic import op

revision = "0005_conversation_document_scope"
down_revision = "0004_retrieval_chat_usage"
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
    op.create_table(
        "conversation_document_scopes",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "conversation_id",
            sa.Uuid(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "document_id",
            sa.Uuid(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "conversation_id", "document_id", name="ux_conversation_document_scope"
        ),
    )
    op.create_index(
        "ix_conversation_document_scopes_user_conversation",
        "conversation_document_scopes",
        ["user_id", "conversation_id"],
    )
    op.execute("ALTER TABLE conversation_document_scopes ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE conversation_document_scopes FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY conversation_document_scopes_owner ON conversation_document_scopes
        USING (user_id::text = current_setting('request.jwt.claim.sub', true))
        WITH CHECK (user_id::text = current_setting('request.jwt.claim.sub', true))
        """
    )
    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_document_scopes TO :runtime_role")


def downgrade() -> None:
    op.drop_index(
        "ix_conversation_document_scopes_user_conversation",
        table_name="conversation_document_scopes",
    )
    op.drop_table("conversation_document_scopes")
