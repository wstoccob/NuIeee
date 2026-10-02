import uuid

from pydantic import Field, computed_field

from schemas.base import CamelModel


class CaseRead(CamelModel):
    id: uuid.UUID
    company: str
    title: str
    description: str
    sort_order: int
    attachment_filename: str | None
    attachment_size_bytes: int | None

    @computed_field
    @property
    def has_attachment(self) -> bool:
        return self.attachment_filename is not None


class CaseWrite(CamelModel):
    company: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=10_000)
    sort_order: int = 0
