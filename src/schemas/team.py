import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from models.team import YearOfStudy
from schemas.base import CamelModel
from schemas.big_event import BigEventRead
from schemas.case import CaseRead

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _collapse_spaces(value: str) -> str:
    return " ".join(value.split())


class MemberInput(CamelModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: str = Field(max_length=255)
    nu_id: str | None = Field(default=None, max_length=32)
    year_of_study: YearOfStudy
    major: str = Field(min_length=1, max_length=255)
    is_captain: bool = False

    @field_validator("full_name", "major")
    @classmethod
    def tidy_text(cls, value: str) -> str:
        return _collapse_spaces(value)

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not _EMAIL.match(value):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("nu_id")
    @classmethod
    def blank_nu_id(cls, value: str | None) -> str | None:
        # The old Google Form asked people to type "-" when they had no NU ID.
        cleaned = (value or "").strip()
        return None if cleaned in {"", "-"} else cleaned


class TeamRegistration(CamelModel):
    team_name: str = Field(min_length=2, max_length=100)
    members: list[MemberInput] = Field(min_length=1, max_length=20)
    consent: Literal[True]
    turnstile_token: str | None = Field(default=None, max_length=2048)
    # Honeypot: hidden from people, so only bots fill it in.
    website: str = Field(default="", max_length=255)

    @field_validator("team_name")
    @classmethod
    def tidy_name(cls, value: str) -> str:
        return _collapse_spaces(value)


class RegistrationResult(CamelModel):
    team_id: uuid.UUID
    access_token: str


class MemberRead(CamelModel):
    full_name: str
    email: str
    nu_id: str | None
    year_of_study: YearOfStudy
    major: str
    is_captain: bool


class SubmissionRead(CamelModel):
    original_filename: str
    content_type: str
    size_bytes: int
    submitted_at: datetime


class TeamDashboard(CamelModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    members: list[MemberRead]
    event: BigEventRead
    case: CaseRead | None
    cases: list[CaseRead]
    submission: SubmissionRead | None
    submission_max_bytes: int


class CaseChoice(CamelModel):
    case_id: uuid.UUID


class UploadRequest(CamelModel):
    filename: str = Field(min_length=1, max_length=255)
    size_bytes: int = Field(gt=0)


class PostUploadTarget(CamelModel):
    """Everything the browser needs for a presigned POST straight to object storage.

    `fields` must be sent as multipart form fields, in order, before the file itself.
    """

    url: str
    fields: dict[str, str]
    object_key: str
    max_bytes: int


class UploadConfirm(CamelModel):
    object_key: str = Field(min_length=1)
    filename: str = Field(min_length=1, max_length=255)


class DownloadLink(CamelModel):
    url: str


class AdminSubmissionRead(SubmissionRead):
    id: uuid.UUID


class AdminTeamRead(CamelModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    members: list[MemberRead]
    case: CaseRead | None
    submission: AdminSubmissionRead | None


class AccessTokenIssued(CamelModel):
    access_token: str
