"""Initial schema: users, events, event_photos

Revision ID: 0001
Revises:
Create Date: 2026-09-19
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "superadmin", name="user_role", native_enum=False),
            nullable=False,
            server_default="admin",
        ),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registration_link", sa.Text(), nullable=True),
    )
    op.create_index("ix_events_starts_at", "events", ["starts_at"])

    op.create_table(
        "event_photos",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "event_id",
            sa.Uuid(),
            sa.ForeignKey("events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("photo_url", sa.Text(), nullable=False),
        sa.Column("alt_text", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_event_photos_event_id", "event_photos", ["event_id"])


def downgrade() -> None:
    op.drop_table("event_photos")
    op.drop_table("events")
    op.drop_table("users")
