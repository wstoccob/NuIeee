from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from core.clock import as_utc
from core.config import settings
from core.errors import ConflictError, InvalidError, NotFoundError
from models.big_event import BigEvent
from models.team import Submission, Team
from schemas.big_event import BigEventRead
from services import storage
from services.uploads import (
    SUBMISSION_TYPES,
    check_size,
    new_key,
    resolve_content_type,
    submission_prefix,
)

# Allows for clock skew between the API and storage when checking the deadline.
_DEADLINE_SKEW = timedelta(seconds=60)


async def _event_for(session: AsyncSession, team: Team) -> BigEvent:
    return await session.get(BigEvent, team.big_event_id)


async def upload_form(session: AsyncSession, team: Team, filename: str, size_bytes: int) -> dict:
    event = await _event_for(session, team)
    if not BigEventRead.model_validate(event).submissions_open:
        raise ConflictError("Submissions are not open")
    if team.case_id is None:
        raise ConflictError("Choose a case before submitting your solution")

    suffix, content_type = resolve_content_type(filename, SUBMISSION_TYPES)
    check_size(size_bytes, settings.submission_max_bytes)

    key = new_key(submission_prefix(event.id, team.id), suffix)
    fields = await storage.private_upload_form(key, content_type, settings.submission_max_bytes)
    return {
        "url": storage.private_bucket_url(),
        "fields": fields,
        "object_key": key,
        "max_bytes": settings.submission_max_bytes,
    }


async def confirm(session: AsyncSession, team: Team, object_key: str, filename: str) -> Team:
    """Record an upload that has already landed in storage.

    The deadline is judged by when storage finished receiving the file, not when this
    call arrives, so a large upload that started on time is not lost to the clock.
    """
    event = await _event_for(session, team)
    if not object_key.startswith(submission_prefix(event.id, team.id)):
        raise InvalidError("That upload does not belong to your team")

    stored = await storage.stat_private(object_key)
    if stored is None:
        raise NotFoundError("The uploaded file was not found. Please upload it again")
    _check_deadline(event, stored.last_modified)
    check_size(stored.size_bytes, settings.submission_max_bytes)

    _, content_type = resolve_content_type(object_key, SUBMISSION_TYPES)
    previous_key = team.submission.object_key if team.submission else None

    if team.submission is None:
        team.submission = Submission(
            object_key=object_key,
            original_filename=filename,
            content_type=content_type,
            size_bytes=stored.size_bytes,
            submitted_at=as_utc(stored.last_modified),
        )
    else:
        team.submission.object_key = object_key
        team.submission.original_filename = filename
        team.submission.content_type = content_type
        team.submission.size_bytes = stored.size_bytes
        team.submission.submitted_at = as_utc(stored.last_modified)

    await session.commit()
    await session.refresh(team)

    if previous_key and previous_key != object_key:
        await storage.delete_private(previous_key)
    return team


def _check_deadline(event: BigEvent, uploaded_at: datetime) -> None:
    opens, closes = event.submissions_open_at, event.submissions_close_at
    if opens is None or closes is None:
        raise ConflictError("Submissions are not open")
    moment = as_utc(uploaded_at)
    if moment < as_utc(opens) - _DEADLINE_SKEW or moment > as_utc(closes) + _DEADLINE_SKEW:
        raise ConflictError("The submission deadline has passed")


async def download_url(team: Team) -> str:
    submission = team.submission
    if submission is None:
        raise NotFoundError("This team has not submitted anything yet")
    suffix = submission.object_key.rsplit(".", 1)[-1]
    case = f" - {team.case.company}" if team.case else ""
    return await storage.private_download_url(submission.object_key, f"{team.name}{case}.{suffix}")
