"""add user_feedback to predictions and global_identifications

Revision ID: 20260427_0003
Revises: 20260427_0002
Create Date: 2026-04-27 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260427_0003"
down_revision = "20260427_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("predictions", sa.Column("user_feedback", sa.Boolean(), nullable=True))
    op.add_column("global_identifications", sa.Column("user_feedback", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("predictions", "user_feedback")
    op.drop_column("global_identifications", "user_feedback")
