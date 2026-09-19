from enum import StrEnum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import TimestampedBase


class Role(StrEnum):
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


_RANK = {Role.ADMIN: 1, Role.SUPERADMIN: 2}


def role_satisfies(actual: Role, minimum: Role) -> bool:
    return _RANK[actual] >= _RANK[minimum]


class User(TimestampedBase):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            name="user_role",
            native_enum=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=Role.ADMIN,
    )
