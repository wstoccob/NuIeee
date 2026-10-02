import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import TimestampedBase


class Case(TimestampedBase):
    """A problem statement a company brings to a hackathon."""

    __tablename__ = "cases"

    big_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("big_events.id", ondelete="CASCADE"), index=True
    )
    company: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    attachment_key: Mapped[str | None] = mapped_column(Text, default=None)
    attachment_filename: Mapped[str | None] = mapped_column(String(255), default=None)
    attachment_size_bytes: Mapped[int | None] = mapped_column(BigInteger, default=None)
