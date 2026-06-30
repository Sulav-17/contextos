from __future__ import annotations

import os

import sqlalchemy as sa

from alembic import op

revision = "0003_document_library"
down_revision = "0002_auth_tenant_isolation"
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
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("extracted_character_count", sa.Integer(), nullable=True),
        sa.Column("failure_code", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('uploaded', 'queued', 'processing', 'ready', 'failed', 'deleted')",
            name="ck_documents_status",
        ),
        sa.CheckConstraint("size_bytes > 0", name="ck_documents_size_positive"),
        sa.CheckConstraint("page_count IS NULL OR page_count > 0", name="ck_documents_page_count"),
        sa.CheckConstraint(
            "extracted_character_count IS NULL OR extracted_character_count >= 0",
            name="ck_documents_extracted_character_count",
        ),
    )
    op.create_index("ux_documents_storage_key", "documents", ["storage_key"], unique=True)
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_user_created", "documents", ["user_id", "created_at"])
    op.create_index("ix_documents_user_status", "documents", ["user_id", "status"])

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "document_id",
            sa.Uuid(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("character_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("chunk_index >= 0", name="ck_document_chunks_chunk_index"),
        sa.CheckConstraint(
            "page_number IS NULL OR page_number > 0", name="ck_document_chunks_page_number"
        ),
        sa.CheckConstraint("character_count > 0", name="ck_document_chunks_character_count"),
        sa.UniqueConstraint("document_id", "chunk_index", name="ux_document_chunks_document_chunk"),
    )
    op.create_index(
        "ix_document_chunks_document_chunk", "document_chunks", ["document_id", "chunk_index"]
    )
    op.create_index(
        "ix_document_chunks_user_document", "document_chunks", ["user_id", "document_id"]
    )

    for table in ("documents", "document_chunks"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY documents_owner ON documents
        USING (user_id::text = current_setting('request.jwt.claim.sub', true))
        WITH CHECK (user_id::text = current_setting('request.jwt.claim.sub', true))
        """
    )
    op.execute(
        """
        CREATE POLICY documents_worker ON documents
        USING (current_setting('app.actor_role', true) = 'worker')
        WITH CHECK (current_setting('app.actor_role', true) = 'worker')
        """
    )
    op.execute(
        """
        CREATE POLICY document_chunks_owner ON document_chunks
        USING (user_id::text = current_setting('request.jwt.claim.sub', true))
        WITH CHECK (
          user_id::text = current_setting('request.jwt.claim.sub', true)
          AND EXISTS (
            SELECT 1
            FROM documents
            WHERE documents.id = document_chunks.document_id
              AND documents.user_id = document_chunks.user_id
          )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY document_chunks_worker ON document_chunks
        USING (current_setting('app.actor_role', true) = 'worker')
        WITH CHECK (current_setting('app.actor_role', true) = 'worker')
        """
    )

    _grant("GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO :runtime_role")
    _grant("GRANT SELECT, INSERT, DELETE ON document_chunks TO :runtime_role")


def downgrade() -> None:
    op.drop_index("ix_document_chunks_user_document", table_name="document_chunks")
    op.drop_index("ix_document_chunks_document_chunk", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_documents_user_status", table_name="documents")
    op.drop_index("ix_documents_user_created", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_index("ux_documents_storage_key", table_name="documents")
    op.drop_table("documents")
