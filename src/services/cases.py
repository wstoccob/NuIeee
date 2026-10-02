import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.errors import InvalidError, NotFoundError
from models.big_event import BigEvent
from models.case import Case
from schemas.case import CaseWrite
from services import storage
from services.uploads import (
    CASE_ATTACHMENT_TYPES,
    case_prefix,
    check_size,
    new_key,
    resolve_content_type,
)


async def list_cases(session: AsyncSession, event_id: uuid.UUID) -> list[Case]:
    stmt = (
        select(Case).where(Case.big_event_id == event_id).order_by(Case.sort_order, Case.created_at)
    )
    return list(await session.scalars(stmt))


async def get_case(session: AsyncSession, case_id: uuid.UUID) -> Case | None:
    return await session.get(Case, case_id)


async def create_case(session: AsyncSession, event: BigEvent, payload: CaseWrite) -> Case:
    case = Case(big_event_id=event.id, **payload.model_dump())
    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


async def update_case(session: AsyncSession, case: Case, payload: CaseWrite) -> Case:
    for field, value in payload.model_dump().items():
        setattr(case, field, value)
    await session.commit()
    await session.refresh(case)
    return case


async def delete_case(session: AsyncSession, case: Case) -> None:
    key = case.attachment_key
    await session.delete(case)
    await session.commit()
    if key:
        await storage.delete_private(key)


async def attachment_upload_form(case: Case, filename: str, size_bytes: int) -> dict:
    suffix, content_type = resolve_content_type(filename, CASE_ATTACHMENT_TYPES)
    check_size(size_bytes, settings.case_attachment_max_bytes)
    key = new_key(case_prefix(case.big_event_id, case.id), suffix)
    fields = await storage.private_upload_form(
        key, content_type, settings.case_attachment_max_bytes
    )
    return {
        "url": storage.private_bucket_url(),
        "fields": fields,
        "object_key": key,
        "max_bytes": settings.case_attachment_max_bytes,
    }


async def attach_file(session: AsyncSession, case: Case, object_key: str, filename: str) -> Case:
    if not object_key.startswith(case_prefix(case.big_event_id, case.id)):
        raise InvalidError("That upload does not belong to this case")
    stored = await storage.stat_private(object_key)
    if stored is None:
        raise NotFoundError("The uploaded file was not found. Please upload it again")

    previous = case.attachment_key
    case.attachment_key = object_key
    case.attachment_filename = filename
    case.attachment_size_bytes = stored.size_bytes
    await session.commit()
    await session.refresh(case)

    if previous and previous != object_key:
        await storage.delete_private(previous)
    return case


async def remove_attachment(session: AsyncSession, case: Case) -> Case:
    key = case.attachment_key
    case.attachment_key = case.attachment_filename = case.attachment_size_bytes = None
    await session.commit()
    await session.refresh(case)
    if key:
        await storage.delete_private(key)
    return case


async def attachment_download_url(case: Case) -> str:
    if not case.attachment_key:
        raise NotFoundError("This case has no attachment")
    return await storage.private_download_url(
        case.attachment_key, case.attachment_filename or "case"
    )
