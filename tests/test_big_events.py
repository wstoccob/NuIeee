from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from models.big_event import BigEvent, BigEventKind


def _make_event(*, slug: str, is_featured: bool) -> BigEvent:
    now = datetime.now(UTC)
    return BigEvent(
        slug=slug,
        title="Test Event",
        kind=BigEventKind.hackathon,
        description="",
        starts_at=now,
        ends_at=now + timedelta(days=1),
        registration_opens_at=now,
        registration_closes_at=now + timedelta(hours=1),
        is_featured=is_featured,
    )


async def test_only_one_big_event_can_be_featured(session):
    session.add(_make_event(slug="event-one", is_featured=True))
    await session.commit()

    session.add(_make_event(slug="event-two", is_featured=True))
    with pytest.raises(IntegrityError):
        await session.commit()
