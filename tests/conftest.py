import os
import sys
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:pw@localhost:5432/nuieee")
os.environ.setdefault("JWT_SECRET", "test-secret-key-at-least-32-chars-long")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "key")
os.environ.setdefault("MINIO_SECRET_KEY", "secret")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.db import get_session
from core.security.passwords import hash_password
from main import app
from models.base import Base
from models.user import Role, User


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session):
    app.dependency_overrides[get_session] = lambda: session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin(session) -> User:
    return await _make_user(session, "admin", Role.ADMIN)


@pytest_asyncio.fixture
async def superadmin(session) -> User:
    return await _make_user(session, "superadmin", Role.SUPERADMIN)


async def _make_user(session, username: str, role: Role) -> User:
    user = User(
        username=username,
        full_name=username.title(),
        password_hash=hash_password("correct-horse-battery"),
        role=role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def auth_header():
    from core.security.jwt import issue_access_token

    def _header(user: User) -> dict[str, str]:
        token = issue_access_token(user.id, user.username, user.role)
        return {"Authorization": f"Bearer {token}"}

    return _header
