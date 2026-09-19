import uuid
from datetime import datetime

from pydantic import Field

from models.user import Role
from schemas.base import CamelModel


class UserRead(CamelModel):
    id: uuid.UUID
    username: str
    full_name: str
    role: Role
    created_at: datetime


class UserCreate(CamelModel):
    username: str = Field(min_length=3, max_length=64)
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=12, max_length=128)
    role: Role = Role.ADMIN
