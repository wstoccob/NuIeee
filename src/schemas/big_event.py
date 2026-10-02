import uuid
from datetime import UTC, datetime

from pydantic import computed_field

from models.big_event import BigEventKind, BigEventStatus
from schemas.base import CamelModel


def _as_aware_utc(value: datetime) -> datetime:
    """SQLite (used in tests) drops timezone info on read; Postgres keeps it.
    Treat a naive datetime as already being UTC so comparisons work either way.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


class BigEventRead(CamelModel):
    id: uuid.UUID
    slug: str
    title: str
    kind: BigEventKind
    description: str
    hero_image_url: str | None
    starts_at: datetime
    ends_at: datetime
    registration_opens_at: datetime
    registration_closes_at: datetime
    capacity: int | None
    status: BigEventStatus

    @computed_field
    @property
    def registration_open(self) -> bool:
        now = datetime.now(UTC)
        opens = _as_aware_utc(self.registration_opens_at)
        closes = _as_aware_utc(self.registration_closes_at)
        return self.status == BigEventStatus.published and opens <= now <= closes
