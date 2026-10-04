import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampedBase


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

    members: Mapped[list["TeamMember"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TeamMember.position",
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
