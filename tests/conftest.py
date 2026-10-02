import os
import sys
from pathlib import Path

# Never read a developer's .env: tests assert against these exact values, and a
# local .env copied from .env.example would silently override them.
os.environ["ENV_FILE"] = ""
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:pw@localhost:5432/nuieee"
os.environ["JWT_SECRET"] = "test-secret-key-at-least-32-chars-long"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "key"
os.environ["MINIO_SECRET_KEY"] = "secret"
os.environ.pop("CORS_ORIGINS", None)
os.environ.pop("CORS_ORIGIN_REGEX", None)
os.environ.pop("MINIO_PUBLIC_BASE_URL", None)
os.environ.pop("MINIO_BUCKET", None)

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


@pytest_asyncio.fixture
async def create_big_event(session):
    from datetime import UTC, datetime, timedelta

    from models.big_event import BigEvent, BigEventKind, BigEventStatus

    async def _create(
        *,
        slug: str,
        status: str = "published",
        is_featured: bool = False,
        title: str = "Test Event",
        kind: BigEventKind = BigEventKind.hackathon,
        starts_at=None,
        ends_at=None,
        registration_opens_at=None,
        registration_closes_at=None,
    ) -> BigEvent:
        now = datetime.now(UTC)
        event = BigEvent(
            slug=slug,
            title=title,
            kind=kind,
            description="",
            status=BigEventStatus(status),
            is_featured=is_featured,
            starts_at=starts_at or now,
            ends_at=ends_at or now + timedelta(days=1),
            registration_opens_at=registration_opens_at or now,
            registration_closes_at=registration_closes_at or now + timedelta(hours=1),
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    return _create


class FakeStorage:
    """In-memory stand-in for the private MinIO bucket."""

    def __init__(self) -> None:
        self.objects: dict[str, tuple[int, str, object]] = {}
        self.deleted: list[str] = []

    def put(self, key: str, size: int = 1024, uploaded_at=None) -> None:
        from datetime import UTC, datetime

        content_type = "application/pdf" if key.endswith(".pdf") else "application/octet-stream"
        self.objects[key] = (size, content_type, uploaded_at or datetime.now(UTC))

    async def upload_form(self, key: str, content_type: str, max_bytes: int) -> dict:
        return {
            "key": key,
            "Content-Type": content_type,
            "policy": "test",
            "x-amz-signature": "sig",
        }

    async def stat(self, key: str):
        from services.storage import StoredObject

        if key not in self.objects:
            return None
        size, content_type, uploaded_at = self.objects[key]
        return StoredObject(size, content_type, uploaded_at)

    async def download_url(self, key: str, name: str) -> str:
        return f"https://storage.test/{key}?download={name}"

    async def delete(self, key: str) -> None:
        self.objects.pop(key, None)
        self.deleted.append(key)

    async def delete_prefix(self, prefix: str) -> None:
        for key in [k for k in self.objects if k.startswith(prefix)]:
            await self.delete(key)


@pytest.fixture
def fake_storage(monkeypatch) -> FakeStorage:
    from services import storage

    fake = FakeStorage()
    monkeypatch.setattr(storage, "private_upload_form", fake.upload_form)
    monkeypatch.setattr(
        storage, "private_bucket_url", lambda: "https://storage.test/hackathon-files"
    )
    monkeypatch.setattr(storage, "stat_private", fake.stat)
    monkeypatch.setattr(storage, "private_download_url", fake.download_url)
    monkeypatch.setattr(storage, "delete_private", fake.delete)
    monkeypatch.setattr(storage, "delete_private_prefix", fake.delete_prefix)
    return fake
