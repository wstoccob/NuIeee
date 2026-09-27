from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.big_event import BigEvent, BigEventStatus


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
