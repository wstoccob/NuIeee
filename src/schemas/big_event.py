import uuid
from datetime import datetime
from typing import Self

from pydantic import AwareDatetime, Field, computed_field, model_validator

from core.clock import within
from models.big_event import BigEventKind, BigEventStatus
from schemas.base import CamelModel

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class BigEventRead(CamelModel):
    id: uuid.UUID
    slug: str
    title: str
    kind: BigEventKind
    description: str
    hero_image_url: str | None
    starts_at: datetime
    ends_at: datetime
    registration_opens_at: datetime
    registration_closes_at: datetime
    capacity: int | None
    status: BigEventStatus
    min_team_size: int
    max_team_size: int

    @computed_field
    @property
    def registration_open(self) -> bool:
        return self.status == BigEventStatus.published and within(
            self.registration_opens_at, self.registration_closes_at
        )


class BigEventAdminRead(BigEventRead):
    is_featured: bool
    team_count: int = 0


class BigEventWrite(CamelModel):
    slug: str = Field(min_length=2, max_length=100, pattern=SLUG_PATTERN)
    title: str = Field(min_length=2, max_length=255)
    kind: BigEventKind = BigEventKind.hackathon
    description: str = ""
    hero_image_url: str | None = None
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    registration_opens_at: AwareDatetime
    registration_closes_at: AwareDatetime
    capacity: int | None = Field(default=None, ge=1)
    status: BigEventStatus = BigEventStatus.draft
    is_featured: bool = False
    min_team_size: int = Field(default=4, ge=1, le=20)
    max_team_size: int = Field(default=5, ge=1, le=20)

    @model_validator(mode="after")
    def check_windows(self) -> Self:
        if self.ends_at < self.starts_at:
            raise ValueError("The event must end after it starts")
        if self.registration_closes_at <= self.registration_opens_at:
            raise ValueError("Registration must close after it opens")
        if self.min_team_size > self.max_team_size:
            raise ValueError("Minimum team size cannot exceed the maximum")
        return self
