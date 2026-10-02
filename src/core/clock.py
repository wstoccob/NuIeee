from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
    """Treat naive datetimes as UTC.

    Postgres timestamptz round-trips with tzinfo, but SQLite (used in tests) drops it,
    and comparing naive with aware datetimes raises TypeError.
    """
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def within(start: datetime | None, end: datetime | None, now: datetime | None = None) -> bool:
    if start is None or end is None:
        return False
    moment = now or utcnow()
    return as_utc(start) <= moment <= as_utc(end)
