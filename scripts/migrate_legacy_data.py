"""Copy data from the legacy ASP.NET tables into the new schema.

The legacy tables use quoted PascalCase identifiers and are therefore distinct
relations from the new lowercase ones, so both live in the same database and
this migration is non-destructive: nothing is dropped, and re-running it is
refused rather than duplicating rows.

Naive legacy timestamps are interpreted as UTC and stored as timestamptz.
Run with --apply to write; the default is a dry run.
"""

import argparse
import asyncio
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from core.security.passwords import hash_password

ALMATY = ZoneInfo("Asia/Almaty")
ROLE_MAP = {"Admin": "admin", "SuperAdmin": "superadmin"}

LEGACY_EVENTS = text("""
    SELECT "Id", "Title", "Description", "EventDateTime", "RegistrationLink", "CreatedAt"
    FROM "Events" ORDER BY "EventDateTime" DESC
""")
LEGACY_PHOTOS = text("""
    SELECT "Id", "EventId", "PhotoLink", "AlternativeText", "CreatedAt"
    FROM "EventPhotos" ORDER BY "CreatedAt"
""")
LEGACY_USERS = text("""
    SELECT u."Id", u."UserName", u."FullName", r."Name" AS role
    FROM "AspNetUsers" u
    LEFT JOIN "AspNetUserRoles" ur ON ur."UserId" = u."Id"
    LEFT JOIN "AspNetRoles" r ON r."Id" = ur."RoleId"
""")


def as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def print_timezone_report(rows) -> None:
    print("\n  Legacy naive value  ->  stored (UTC)          ->  displays in Almaty")
    print("  " + "-" * 74)
    for row in rows:
        utc = as_utc(row.EventDateTime)
        local = utc.astimezone(ALMATY)
        title = row.Title[:28]
        print(
            f"  {row.EventDateTime:%Y-%m-%d %H:%M}"
            f"  ->  {utc:%Y-%m-%d %H:%M %Z}"
            f"  ->  {local:%Y-%m-%d %H:%M}  {title}"
        )


async def fetch_legacy(conn):
    events = (await conn.execute(LEGACY_EVENTS)).all()
    photos = (await conn.execute(LEGACY_PHOTOS)).all()
    users = (await conn.execute(LEGACY_USERS)).all()
    return events, photos, users


async def target_is_empty(conn) -> bool:
    counts = (
        await conn.execute(
            text("SELECT (SELECT count(*) FROM events) + (SELECT count(*) FROM users) AS n")
        )
    ).scalar_one()
    return counts == 0


async def insert_events(conn, events, photos) -> None:
    for row in events:
        await conn.execute(
            text("""
                INSERT INTO events
                    (id, title, description, starts_at, registration_link, created_at)
                VALUES (:id, :title, :description, :starts_at, :link, :created_at)
            """),
            {
                "id": row.Id,
                "title": row.Title,
                "description": row.Description or "",
                "starts_at": as_utc(row.EventDateTime),
                "link": row.RegistrationLink,
                "created_at": as_utc(row.CreatedAt),
            },
        )

    for row in photos:
        await conn.execute(
            text("""
                INSERT INTO event_photos
                    (id, event_id, photo_url, alt_text, created_at)
                VALUES (:id, :event_id, :url, :alt, :created_at)
            """),
            {
                "id": row.Id,
                "event_id": row.EventId,
                "url": row.PhotoLink,
                "alt": row.AlternativeText or "",
                "created_at": as_utc(row.CreatedAt),
            },
        )


async def insert_users(conn, users) -> list[tuple[str, str]]:
    """Recreate accounts with fresh Argon2 passwords.

    ASP.NET Identity hashes are PBKDF2 in a Microsoft-specific envelope and are
    not portable, so the two service accounts get new generated passwords.
    """
    credentials = []
    for row in users:
        password = secrets.token_urlsafe(16)
        await conn.execute(
            text("""
                INSERT INTO users (id, username, full_name, password_hash, role)
                VALUES (:id, :username, :full_name, :password_hash, :role)
            """),
            {
                "id": row.Id,
                "username": row.UserName,
                "full_name": row.FullName or row.UserName,
                "password_hash": hash_password(password),
                "role": ROLE_MAP.get(row.role, "admin"),
            },
        )
        credentials.append((row.UserName, password))
    return credentials


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    engine = create_async_engine(args.dsn)
    async with engine.begin() as conn:
        events, photos, users = await fetch_legacy(conn)

        print(f"Legacy rows: {len(events)} events, {len(photos)} photos, {len(users)} users")
        print_timezone_report(events)

        if not args.apply:
            print("\nDRY RUN - nothing written. Re-run with --apply to migrate.")
            await engine.dispose()
            return 0

        if not await target_is_empty(conn):
            print("\nREFUSED: target tables already contain rows.")
            await engine.dispose()
            return 1

        await insert_events(conn, events, photos)
        credentials = await insert_users(conn, users)

    await engine.dispose()

    print("\nMigration applied. Generated passwords (save these now):")
    for username, password in credentials:
        print(f"  {username:12} {password}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
