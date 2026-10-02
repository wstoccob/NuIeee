import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampedBase, utcnow
from models.case import Case


class YearOfStudy(StrEnum):
    FIRST = "1"
    SECOND = "2"
    THIRD = "3"
    FOURTH = "4"
    NOT_APPLICABLE = "na"


class Team(TimestampedBase):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("big_event_id", "name_key", name="uq_team_name_per_event"),)

    big_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("big_events.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    # Lowercased copy for case-insensitive uniqueness that also works on SQLite.
    name_key: Mapped[str] = mapped_column(String(100))
    # SHA-256 of the access token. The token itself is shown once and never stored.
    access_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cases.id", ondelete="SET NULL"), default=None
    )

    members: Mapped[list["TeamMember"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TeamMember.position",
    )
    case: Mapped[Case | None] = relationship(lazy="selectin")
    submission: Mapped["Submission | None"] = relationship(
        back_populates="team", cascade="all, delete-orphan", lazy="selectin", uselist=False
    )


class TeamMember(TimestampedBase):
    __tablename__ = "team_members"

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(default=0)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    nu_id: Mapped[str | None] = mapped_column(String(32), default=None)
    year_of_study: Mapped[YearOfStudy] = mapped_column(
        Enum(
            YearOfStudy,
            name="year_of_study",
            native_enum=False,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    major: Mapped[str] = mapped_column(String(255))
    is_captain: Mapped[bool] = mapped_column(Boolean, default=False)

    team: Mapped[Team] = relationship(back_populates="members")


class Submission(TimestampedBase):
    __tablename__ = "submissions"

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), unique=True
    )
    object_key: Mapped[str] = mapped_column(Text)
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(127))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team: Mapped[Team] = relationship(back_populates="submission")
