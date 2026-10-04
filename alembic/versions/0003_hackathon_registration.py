"""Hackathon registration: team size limits, teams and members

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.add_column(
        "big_events", sa.Column("min_team_size", sa.Integer(), nullable=False, server_default="4")
    )
    op.add_column(
        "big_events", sa.Column("max_team_size", sa.Integer(), nullable=False, server_default="5")
    )

    op.create_table(
        "teams",
        *_timestamps(),
        sa.Column(
            "big_event_id",
            sa.Uuid(),
            sa.ForeignKey("big_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_key", sa.String(100), nullable=False),
        sa.UniqueConstraint("big_event_id", "name_key", name="uq_team_name_per_event"),
    )
    op.create_index("ix_teams_big_event_id", "teams", ["big_event_id"])

    op.create_table(
        "team_members",
        *_timestamps(),
        sa.Column(
            "team_id", sa.Uuid(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("nu_id", sa.String(32), nullable=True),
        sa.Column(
            "year_of_study",
            sa.Enum("1", "2", "3", "4", "na", name="year_of_study", native_enum=False),
            nullable=False,
        ),
        sa.Column("major", sa.String(255), nullable=False),
        sa.Column("is_captain", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_team_members_team_id", "team_members", ["team_id"])


def downgrade() -> None:
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_column("big_events", "max_team_size")
    op.drop_column("big_events", "min_team_size")
