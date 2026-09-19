import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampedBase


class Event(TimestampedBase):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    registration_link: Mapped[str | None] = mapped_column(Text, default=None)

    photos: Mapped[list["EventPhoto"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="EventPhoto.created_at",
    )


class EventPhoto(TimestampedBase):
    __tablename__ = "event_photos"

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), index=True
    )
    photo_url: Mapped[str] = mapped_column(Text)
    alt_text: Mapped[str] = mapped_column(Text, default="")

    event: Mapped[Event] = relationship(back_populates="photos")
