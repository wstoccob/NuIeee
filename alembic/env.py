import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from core.config import settings
from models import event, user  # noqa: F401  (register tables on Base.metadata)
from models.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.dsn)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# The legacy ASP.NET tables use quoted PascalCase identifiers and are distinct
# relations from the new lowercase ones. They are dropped manually at cutover,
# so autogenerate must never propose removing them.
LEGACY_TABLES = {
    "Events",
    "EventPhotos",
    "Teams",
    "TeamMembers",
    "__EFMigrationsHistory",
    "AspNetUsers",
    "AspNetRoles",
    "AspNetUserRoles",
    "AspNetUserClaims",
    "AspNetUserLogins",
    "AspNetUserTokens",
    "AspNetRoleClaims",
}


def include_object(obj, name, type_, reflected, compare_to) -> bool:
    return not (type_ == "table" and name in LEGACY_TABLES)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.dsn,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _run(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with engine.connect() as connection:
        await connection.run_sync(_run)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
