import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.event import Event, EventPhoto
from schemas.event import EventWrite


async def list_events(session: AsyncSession, limit: int | None = None) -> list[Event]:
    stmt = select(Event).order_by(Event.starts_at.desc())
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.scalars(stmt)
    return list(result)


async def get_event(session: AsyncSession, event_id: uuid.UUID) -> Event | None:
    return await session.get(Event, event_id)


async def create_event(session: AsyncSession, payload: EventWrite) -> Event:
    event = Event(
        title=payload.title,
        description=payload.description,
        starts_at=payload.starts_at,
        registration_link=str(payload.registration_link) if payload.registration_link else None,
        photos=[_photo(p) for p in payload.photos],
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def replace_event(session: AsyncSession, event: Event, payload: EventWrite) -> Event:
    """Overwrite an event in place.

    Photos are replaced wholesale: delete-orphan on the relationship removes rows
    dropped from the payload, which the previous EF implementation silently leaked.
    """
    event.title = payload.title
    event.description = payload.description
    event.starts_at = payload.starts_at
    event.registration_link = str(payload.registration_link) if payload.registration_link else None
    event.photos = [_photo(p) for p in payload.photos]

    await session.commit()
    await session.refresh(event)
    return event


async def delete_event(session: AsyncSession, event: Event) -> None:
    await session.delete(event)
    await session.commit()


def _photo(payload) -> EventPhoto:
    return EventPhoto(photo_url=payload.photo_url, alt_text=payload.alt_text)
