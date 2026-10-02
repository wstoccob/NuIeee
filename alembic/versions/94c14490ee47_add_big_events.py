"""add big_events

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-27
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "big_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("hackathon", "conference", name="big_event_kind", native_enum=False),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("hero_image_url", sa.Text(), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registration_opens_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registration_closes_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "published", "archived", name="big_event_status", native_enum=False),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_big_events_slug", "big_events", ["slug"], unique=True)
    op.create_index("ix_big_events_starts_at", "big_events", ["starts_at"])

    # Only one event may be featured at a time.
    # Enforced by the database itself, not by application code.
    op.execute(
        "CREATE UNIQUE INDEX one_featured_big_event ON big_events ((true)) WHERE is_featured"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS one_featured_big_event")
    op.drop_table("big_events")
