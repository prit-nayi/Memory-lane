"""Add admin users, visitor disablement, and slideshow settings.

Revision ID: 20261111_04
Revises: 20261111_03
Create Date: 2026-11-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261111_04"
down_revision: Union[str, None] = "20261111_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "visitors",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
    )
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_admin_users_username"),
    )
    op.create_table(
        "slideshow_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "slide_duration_seconds",
            sa.Integer(),
            server_default="7",
            nullable=False,
        ),
        sa.Column(
            "refresh_interval_seconds",
            sa.Integer(),
            server_default="5",
            nullable=False,
        ),
        sa.Column(
            "fade_duration_ms",
            sa.Integer(),
            server_default="750",
            nullable=False,
        ),
        sa.Column(
            "allow_shuffle",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "allow_fullscreen",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "slide_duration_seconds BETWEEN 3 AND 30",
            name="ck_slideshow_settings_slide_duration",
        ),
        sa.CheckConstraint(
            "refresh_interval_seconds BETWEEN 5 AND 300",
            name="ck_slideshow_settings_refresh_interval",
        ),
        sa.CheckConstraint(
            "fade_duration_ms BETWEEN 250 AND 2000",
            name="ck_slideshow_settings_fade_duration",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("slideshow_settings")
    op.drop_table("admin_users")
    op.drop_column("visitors", "is_active")
