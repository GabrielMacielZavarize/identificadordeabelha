"""initial schema

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260417_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "species",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("scientific_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_species_code", "species", ["code"], unique=True)
    op.create_index("ix_species_is_active", "species", ["is_active"], unique=False)

    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version", sa.String(length=100), nullable=False),
        sa.Column("encoder_name", sa.String(length=255), nullable=False),
        sa.Column("classifier_type", sa.String(length=100), nullable=False),
        sa.Column("artifact_dir", sa.String(length=500), nullable=False),
        sa.Column("metrics_json", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_model_versions_is_active", "model_versions", ["is_active"], unique=False)
    op.create_index("ix_model_versions_version", "model_versions", ["version"], unique=True)

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("predicted_species_id", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("probabilities_json", sa.Text(), nullable=False),
        sa.Column("model_version_id", sa.Integer(), nullable=False),
        sa.Column("inference_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"]),
        sa.ForeignKeyConstraint(["predicted_species_id"], ["species.id"]),
    )
    op.create_index("ix_predictions_created_at", "predictions", ["created_at"], unique=False)
    op.create_index("ix_predictions_sha256", "predictions", ["sha256"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_predictions_sha256", table_name="predictions")
    op.drop_index("ix_predictions_created_at", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_model_versions_version", table_name="model_versions")
    op.drop_index("ix_model_versions_is_active", table_name="model_versions")
    op.drop_table("model_versions")
    op.drop_index("ix_species_is_active", table_name="species")
    op.drop_index("ix_species_code", table_name="species")
    op.drop_table("species")
