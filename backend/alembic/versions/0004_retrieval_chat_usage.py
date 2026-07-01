from __future__ import annotations

import os

import sqlalchemy as sa

from alembic import op

revision = "0004_retrieval_chat_usage"
down_revision = "0003_document_library"
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
    op.add_column("document_chunks", sa.Column("content_sha256", sa.Text(), nullable=True))
    op.add_column("document_chunks", sa.Column("embedding", sa.Text(), nullable=True))
    op.add_column("document_chunks", sa.Column("embedding_provider", sa.Text(), nullable=True))
    op.add_column("document_chunks", sa.Column("embedding_model", sa.Text(), nullable=True))
    op.add_column("document_chunks", sa.Column("embedding_dimension", sa.Integer(), nullable=True))
    op.add_column(
        "document_chunks",
        sa.Column("embedding_created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE document_chunks
        SET content_sha256 = encode(digest(content, 'sha256'), 'hex')
        WHERE content_sha256 IS NULL
        """
    )
    op.alter_column("document_chunks", "content_sha256", nullable=False)
    op.execute(
        """
        ALTER TABLE document_chunks
        ALTER COLUMN embedding TYPE vector(768) USING embedding::vector
        """
    )
    op.create_index(
        "ix_document_chunks_embedding_model", "document_chunks", ["user_id", "embedding_model"]
    )
    op.execute(
        """
        CREATE INDEX ix_document_chunks_embedding_vector
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        WHERE embedding IS NOT NULL
        """
    )
    op.create_check_constraint(
        "ck_document_chunks_embedding_complete",
        "document_chunks",
        """
        (
          embedding IS NULL
          AND embedding_provider IS NULL
          AND embedding_model IS NULL
          AND embedding_dimension IS NULL
          AND embedding_created_at IS NULL
        )
        OR
        (
          embedding IS NOT NULL
          AND embedding_provider IS NOT NULL
          AND embedding_model IS NOT NULL
          AND embedding_dimension IS NOT NULL
          AND embedding_created_at IS NOT NULL
        )
        """,
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("length(title) BETWEEN 1 AND 120", name="ck_conversations_title_length"),
    )
    op.create_index("ix_conversations_user_updated", "conversations", ["user_id", "updated_at"])

    op.create_table(
        "messages",
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
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=True),
        sa.Column("model", sa.Text(), nullable=True),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="ck_messages_role"),
        sa.CheckConstraint(
            "status IN ('accepted', 'completed', 'failed')", name="ck_messages_status"
        ),
        sa.CheckConstraint(
            "length(content) BETWEEN 1 AND 12000", name="ck_messages_content_length"
        ),
    )
    op.create_index(
        "ix_messages_conversation_created", "messages", ["conversation_id", "created_at"]
    )
    op.create_index("ix_messages_user_created", "messages", ["user_id", "created_at"])

    op.create_table(
        "message_citations",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "message_id",
            sa.Uuid(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
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
            "chunk_id",
            sa.Uuid(),
            sa.ForeignKey("document_chunks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("citation_index", sa.Integer(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("page_number > 0", name="ck_message_citations_page"),
        sa.CheckConstraint("citation_index > 0", name="ck_message_citations_index"),
        sa.CheckConstraint(
            "length(excerpt) BETWEEN 1 AND 700", name="ck_message_citations_excerpt"
        ),
        sa.UniqueConstraint("message_id", "citation_index", name="ux_message_citations_order"),
    )
    op.create_index(
        "ix_message_citations_message", "message_citations", ["message_id", "citation_index"]
    )
    op.create_index("ix_message_citations_user", "message_citations", ["user_id"])

    op.create_table(
        "usage_counters",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("period_type", sa.Text(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("period_type IN ('daily', 'monthly')", name="ck_usage_counters_period"),
        sa.CheckConstraint("message_count >= 0", name="ck_usage_counters_count"),
        sa.UniqueConstraint(
            "user_id", "period_type", "period_start", name="ux_usage_counters_period"
        ),
    )
    op.create_index("ix_usage_counters_user", "usage_counters", ["user_id"])

    for table in ("conversations", "messages", "message_citations", "usage_counters"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    for table in ("conversations", "messages", "message_citations", "usage_counters"):
        op.execute(
            f"""
            CREATE POLICY {table}_owner ON {table}
            USING (user_id::text = current_setting('request.jwt.claim.sub', true))
            WITH CHECK (user_id::text = current_setting('request.jwt.claim.sub', true))
            """
        )

    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON document_chunks TO :runtime_role")
    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON conversations TO :runtime_role")
    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON messages TO :runtime_role")
    _grant("GRANT SELECT, INSERT, DELETE ON message_citations TO :runtime_role")
    _grant("GRANT SELECT, INSERT, UPDATE ON usage_counters TO :runtime_role")


def downgrade() -> None:
    op.drop_index("ix_usage_counters_user", table_name="usage_counters")
    op.drop_table("usage_counters")
    op.drop_index("ix_message_citations_user", table_name="message_citations")
    op.drop_index("ix_message_citations_message", table_name="message_citations")
    op.drop_table("message_citations")
    op.drop_index("ix_messages_user_created", table_name="messages")
    op.drop_index("ix_messages_conversation_created", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_conversations_user_updated", table_name="conversations")
    op.drop_table("conversations")
    op.drop_index("ix_document_chunks_embedding_vector", table_name="document_chunks")
    op.drop_index("ix_document_chunks_embedding_model", table_name="document_chunks")
    op.drop_column("document_chunks", "embedding_created_at")
    op.drop_column("document_chunks", "embedding_dimension")
    op.drop_column("document_chunks", "embedding_model")
    op.drop_column("document_chunks", "embedding_provider")
    op.drop_column("document_chunks", "embedding")
    op.drop_column("document_chunks", "content_sha256")
