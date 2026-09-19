import uuid
from datetime import datetime

from pydantic import Field, HttpUrl, computed_field

from schemas.base import CamelModel


class EventPhotoRead(CamelModel):
    id: uuid.UUID
    photo_url: str
    alt_text: str


class EventPhotoWrite(CamelModel):
    photo_url: str = Field(min_length=1)
    alt_text: str = ""


class EventRead(CamelModel):
    id: uuid.UUID
    title: str
    description: str
    starts_at: datetime
    registration_link: str | None
    photos: list[EventPhotoRead]

    @computed_field
    @property
    def has_registration_link(self) -> bool:
        return self.registration_link is not None


class EventWrite(CamelModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    starts_at: datetime
    registration_link: HttpUrl | None = None
    photos: list[EventPhotoWrite] = Field(default_factory=list)
