"""add global identifications

Revision ID: 20260427_0002
Revises: 20260417_0001
Create Date: 2026-04-27 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260427_0002"
down_revision = "20260417_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "global_identifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("predicted_code", sa.String(length=100), nullable=False),
        sa.Column("predicted_scientific_name", sa.String(length=255), nullable=False),
        sa.Column("predicted_common_name", sa.String(length=255), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("probabilities_json", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("inference_ms", sa.Float(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_global_identifications_created_at",
        "global_identifications",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_global_identifications_sha256",
        "global_identifications",
        ["sha256"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_global_identifications_sha256", table_name="global_identifications")
    op.drop_index("ix_global_identifications_created_at", table_name="global_identifications")
    op.drop_table("global_identifications")
