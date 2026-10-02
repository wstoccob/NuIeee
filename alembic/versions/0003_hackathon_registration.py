"""Hackathon registration: cases, teams, members, submissions

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
    for column in ("case_selection_opens_at", "submissions_open_at", "submissions_close_at"):
        op.add_column("big_events", sa.Column(column, sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "cases",
        *_timestamps(),
        sa.Column(
            "big_event_id",
            sa.Uuid(),
            sa.ForeignKey("big_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attachment_key", sa.Text(), nullable=True),
        sa.Column("attachment_filename", sa.String(255), nullable=True),
        sa.Column("attachment_size_bytes", sa.BigInteger(), nullable=True),
    )
    op.create_index("ix_cases_big_event_id", "cases", ["big_event_id"])

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
        sa.Column("access_token_hash", sa.String(64), nullable=False),
        sa.Column(
            "case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="SET NULL"), nullable=True
        ),
        sa.UniqueConstraint("big_event_id", "name_key", name="uq_team_name_per_event"),
    )
    op.create_index("ix_teams_big_event_id", "teams", ["big_event_id"])
    op.create_index("ix_teams_access_token_hash", "teams", ["access_token_hash"], unique=True)

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

    op.create_table(
        "submissions",
        *_timestamps(),
        sa.Column(
            "team_id",
            sa.Uuid(),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("object_key", sa.Text(), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(127), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("submissions")
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_table("cases")
    for column in (
        "submissions_close_at",
        "submissions_open_at",
        "case_selection_opens_at",
        "max_team_size",
        "min_team_size",
    ):
        op.drop_column("big_events", column)
