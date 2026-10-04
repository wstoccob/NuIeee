import uuid

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.errors import ConflictError
from models.big_event import BigEvent, BigEventStatus
from models.team import Team
from schemas.big_event import BigEventWrite


async def get_featured_big_event(session: AsyncSession) -> BigEvent | None:
    stmt = select(BigEvent).where(
        BigEvent.is_featured.is_(True),
        BigEvent.status == BigEventStatus.published,
    )
    result = await session.scalars(stmt)
    return result.first()


async def get_big_event_by_slug(session: AsyncSession, slug: str) -> BigEvent | None:
    stmt = select(BigEvent).where(BigEvent.slug == slug)
    result = await session.scalars(stmt)
    return result.first()


async def get_big_event(session: AsyncSession, event_id: uuid.UUID) -> BigEvent | None:
    return await session.get(BigEvent, event_id)


async def list_big_events(session: AsyncSession) -> list[tuple[BigEvent, int]]:
    team_count = (
        select(Team.big_event_id, func.count(Team.id).label("n"))
        .group_by(Team.big_event_id)
        .subquery()
    )
    stmt = (
        select(BigEvent, func.coalesce(team_count.c.n, 0))
        .outerjoin(team_count, team_count.c.big_event_id == BigEvent.id)
        .order_by(BigEvent.starts_at.desc())
    )
    return [(event, count) for event, count in (await session.execute(stmt)).all()]


async def count_teams(session: AsyncSession, event_id: uuid.UUID) -> int:
    stmt = select(func.count(Team.id)).where(Team.big_event_id == event_id)
    return (await session.scalar(stmt)) or 0


async def create_big_event(session: AsyncSession, payload: BigEventWrite) -> BigEvent:
    event = BigEvent(**payload.model_dump())
    if payload.is_featured:
        await _unfeature_others(session, keep=None)
    session.add(event)
    await _commit(session)
    await session.refresh(event)
    return event


async def update_big_event(
    session: AsyncSession, event: BigEvent, payload: BigEventWrite
) -> BigEvent:
    if payload.is_featured and not event.is_featured:
        await _unfeature_others(session, keep=event.id)
    for field, value in payload.model_dump().items():
        setattr(event, field, value)
    await _commit(session)
    await session.refresh(event)
    return event


async def delete_big_event(session: AsyncSession, event: BigEvent) -> None:
    await session.delete(event)
    await session.commit()


async def _unfeature_others(session: AsyncSession, keep: uuid.UUID | None) -> None:
    stmt = update(BigEvent).where(BigEvent.is_featured.is_(True)).values(is_featured=False)
    if keep is not None:
        stmt = stmt.where(BigEvent.id != keep)
    await session.execute(stmt)
    await session.flush()


async def _commit(session: AsyncSession) -> None:
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ConflictError("Another event already uses that slug") from exc
