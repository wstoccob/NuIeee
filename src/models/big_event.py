import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import TimestampedBase


class BigEventKind(enum.StrEnum):
    hackathon = "hackathon"
    conference = "conference"


class BigEventStatus(enum.StrEnum):
    draft = "draft"
    published = "published"
    archived = "archived"


class BigEvent(TimestampedBase):
    __tablename__ = "big_events"
    __table_args__ = (
        Index(
            "one_featured_big_event",
            "is_featured",
            unique=True,
            postgresql_where=text("is_featured"),
            sqlite_where=text("is_featured"),
        ),
    )

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    kind: Mapped[BigEventKind] = mapped_column(
        Enum(BigEventKind, name="big_event_kind", native_enum=False)
    )
    description: Mapped[str] = mapped_column(Text, default="")
    hero_image_url: Mapped[str | None] = mapped_column(Text, default=None)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_opens_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    capacity: Mapped[int | None] = mapped_column(Integer, default=None)

    min_team_size: Mapped[int] = mapped_column(Integer, default=4, server_default="4")
    max_team_size: Mapped[int] = mapped_column(Integer, default=5, server_default="5")
    status: Mapped[BigEventStatus] = mapped_column(
        Enum(BigEventStatus, name="big_event_status", native_enum=False),
        default=BigEventStatus.draft,
        server_default=BigEventStatus.draft.value,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
