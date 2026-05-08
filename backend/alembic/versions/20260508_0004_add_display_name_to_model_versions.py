"""add display_name to model_versions

Revision ID: 20260508_0004
Revises: 20260427_0003
Create Date: 2026-05-08 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260508_0004"
down_revision = "20260427_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("model_versions", sa.Column("display_name", sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column("model_versions", "display_name")
