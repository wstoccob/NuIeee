import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.passwords import hash_password
from models.user import Role, User
from schemas.user import UserCreate


async def list_users(session: AsyncSession) -> list[User]:
    result = await session.scalars(select(User).order_by(User.created_at))
    return list(result)


async def get_user(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def get_by_username(session: AsyncSession, username: str) -> User | None:
    return await session.scalar(select(User).where(User.username == username))


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    user = User(
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()


def is_last_superadmin(users: list[User], target: User) -> bool:
    if target.role is not Role.SUPERADMIN:
        return False
    return sum(1 for u in users if u.role is Role.SUPERADMIN) <= 1
