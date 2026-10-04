import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from models.team import YearOfStudy
from schemas.base import CamelModel

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


class MemberRead(CamelModel):
    full_name: str
    email: str
    nu_id: str | None
    year_of_study: YearOfStudy
    major: str
    is_captain: bool


class AdminTeamRead(CamelModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    members: list[MemberRead]
