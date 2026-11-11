"""Publish all photos immediately without moderation status.

Revision ID: 20261111_03
Revises: 20261111_02
Create Date: 2026-11-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261111_03"
down_revision: Union[str, None] = "20261111_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_photos_status", "photos", type_="check")
    op.drop_column("photos", "status")


def downgrade() -> None:
    op.add_column(
        "photos",
        sa.Column(
            "status",
            sa.String(length=8),
            server_default="pending",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_photos_status",
        "photos",
        "status IN ('pending', 'approved', 'rejected')",
    )
