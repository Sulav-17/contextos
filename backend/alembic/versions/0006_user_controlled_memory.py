from __future__ import annotations

import os

import sqlalchemy as sa

from alembic import op

revision = "0006_user_controlled_memory"
down_revision = "0005_conversation_document_scope"
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
    op.add_column("conversations", sa.Column("archived_at", sa.DateTime(timezone=True)))
    op.create_index(
        "ix_conversations_user_archived_updated",
        "conversations",
        ["user_id", "archived_at", "updated_at"],
    )

    op.create_table(
        "memories",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("memory_type", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("source_kind", sa.Text(), nullable=False),
        sa.Column(
            "source_conversation_id",
            sa.Uuid(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "source_message_id",
            sa.Uuid(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("content_sha256", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "memory_type IN ('identity', 'background', 'goal', 'preference', 'project', "
            "'decision', 'constraint', 'other')",
            name="ck_memories_type",
        ),
        sa.CheckConstraint(
            "status IN ('suggested', 'approved', 'disabled', 'rejected')",
            name="ck_memories_status",
        ),
        sa.CheckConstraint("source_kind IN ('manual', 'conversation')", name="ck_memories_source"),
        sa.CheckConstraint("length(content) BETWEEN 1 AND 1200", name="ck_memories_content"),
        sa.CheckConstraint("length(content_sha256) = 64", name="ck_memories_content_hash"),
        sa.CheckConstraint(
            """
            (
              source_kind = 'manual'
              AND source_conversation_id IS NULL
              AND source_message_id IS NULL
            )
            OR
            (
              source_kind = 'conversation'
              AND source_conversation_id IS NOT NULL
              AND source_message_id IS NOT NULL
            )
            """,
            name="ck_memories_source_provenance",
        ),
        sa.UniqueConstraint("user_id", "content_sha256", name="ux_memories_user_content"),
    )
    op.create_index(
        "ix_memories_user_status_updated", "memories", ["user_id", "status", "updated_at"]
    )
    op.create_index(
        "ix_memories_user_active",
        "memories",
        ["user_id", "updated_at"],
        postgresql_where=sa.text("status = 'approved' AND deleted_at IS NULL"),
    )

    op.create_table(
        "memory_embeddings",
        sa.Column(
            "memory_id",
            sa.Uuid(),
            sa.ForeignKey("memories.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("embedding", sa.Text(), nullable=False),
        sa.Column("embedding_provider", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.Text(), nullable=False),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False),
        sa.Column("content_sha256", sa.Text(), nullable=False),
        sa.Column(
            "embedding_created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("embedding_dimension > 0", name="ck_memory_embeddings_dimension"),
        sa.CheckConstraint(
            "length(content_sha256) = 64", name="ck_memory_embeddings_content_hash"
        ),
    )
    op.execute(
        """
        ALTER TABLE memory_embeddings
        ALTER COLUMN embedding TYPE vector(768) USING embedding::vector
        """
    )
    op.create_index(
        "ix_memory_embeddings_user_model",
        "memory_embeddings",
        ["user_id", "embedding_model"],
    )
    op.execute(
        """
        CREATE INDEX ix_memory_embeddings_vector
        ON memory_embeddings
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )

    op.create_table(
        "message_memory_references",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "message_id",
            sa.Uuid(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "memory_id",
            sa.Uuid(),
            sa.ForeignKey("memories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("memory_type", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_conversation_id", sa.Uuid(), nullable=True),
        sa.Column("reference_index", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("reference_index > 0", name="ck_message_memory_references_index"),
        sa.CheckConstraint(
            "length(content) BETWEEN 1 AND 1200", name="ck_message_memory_references_content"
        ),
        sa.UniqueConstraint(
            "message_id", "reference_index", name="ux_message_memory_references_order"
        ),
    )
    op.create_index(
        "ix_message_memory_references_message",
        "message_memory_references",
        ["message_id", "reference_index"],
    )

    for table in ("memories", "memory_embeddings", "message_memory_references"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY {table}_owner ON {table}
            USING (user_id::text = current_setting('request.jwt.claim.sub', true))
            WITH CHECK (user_id::text = current_setting('request.jwt.claim.sub', true))
            """
        )

    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON conversations TO :runtime_role")
    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON memories TO :runtime_role")
    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON memory_embeddings TO :runtime_role")
    _grant("GRANT SELECT, INSERT, DELETE ON message_memory_references TO :runtime_role")


def downgrade() -> None:
    op.drop_index(
        "ix_message_memory_references_message", table_name="message_memory_references"
    )
    op.drop_table("message_memory_references")
    op.drop_index("ix_memory_embeddings_vector", table_name="memory_embeddings")
    op.drop_index("ix_memory_embeddings_user_model", table_name="memory_embeddings")
    op.drop_table("memory_embeddings")
    op.drop_index("ix_memories_user_active", table_name="memories")
    op.drop_index("ix_memories_user_status_updated", table_name="memories")
    op.drop_table("memories")
    op.drop_index("ix_conversations_user_archived_updated", table_name="conversations")
    op.drop_column("conversations", "archived_at")
