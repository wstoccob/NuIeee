import uuid
from datetime import datetime
from typing import Self

from pydantic import AwareDatetime, Field, computed_field, model_validator

from core.clock import as_utc, utcnow, within
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
    case_selection_opens_at: datetime | None
    submissions_open_at: datetime | None
    submissions_close_at: datetime | None

    def _is_published(self) -> bool:
        return self.status == BigEventStatus.published

    @computed_field
    @property
    def registration_open(self) -> bool:
        return self._is_published() and within(
            self.registration_opens_at, self.registration_closes_at
        )

    @computed_field
    @property
    def cases_visible(self) -> bool:
        opens = self.case_selection_opens_at
        return self._is_published() and opens is not None and utcnow() >= as_utc(opens)

    @computed_field
    @property
    def case_selection_open(self) -> bool:
        if not self.cases_visible:
            return False
        closes = self.submissions_close_at
        return closes is None or utcnow() <= as_utc(closes)

    @computed_field
    @property
    def submissions_open(self) -> bool:
        return self._is_published() and within(self.submissions_open_at, self.submissions_close_at)


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
    case_selection_opens_at: AwareDatetime | None = None
    submissions_open_at: AwareDatetime | None = None
    submissions_close_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def check_windows(self) -> Self:
        if self.ends_at < self.starts_at:
            raise ValueError("The event must end after it starts")
        if self.registration_closes_at <= self.registration_opens_at:
            raise ValueError("Registration must close after it opens")
        if self.min_team_size > self.max_team_size:
            raise ValueError("Minimum team size cannot exceed the maximum")
        if (self.submissions_open_at is None) != (self.submissions_close_at is None):
            raise ValueError("Set both submission dates, or neither")
        if self.submissions_open_at and self.submissions_close_at <= self.submissions_open_at:
            raise ValueError("Submissions must close after they open")
        return self
