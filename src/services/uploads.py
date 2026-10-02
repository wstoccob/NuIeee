import uuid
from pathlib import PurePosixPath

from core.errors import InvalidError

PDF = "application/pdf"
PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ZIP = "application/zip"

# Content type is derived from the extension on the server, never taken from the
# browser: some browsers report an empty type for .pptx.
SUBMISSION_TYPES = {".pdf": PDF, ".pptx": PPTX}
CASE_ATTACHMENT_TYPES = {".pdf": PDF, ".pptx": PPTX, ".docx": DOCX, ".xlsx": XLSX, ".zip": ZIP}


def resolve_content_type(filename: str, allowed: dict[str, str]) -> tuple[str, str]:
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix not in allowed:
        names = ", ".join(ext.lstrip(".").upper() for ext in allowed)
        raise InvalidError(f"This file type is not accepted. Allowed: {names}")
    return suffix, allowed[suffix]


def check_size(size_bytes: int, max_bytes: int) -> None:
    if size_bytes > max_bytes:
        raise InvalidError(f"The file is too large. The limit is {max_bytes // (1024 * 1024)} MB")


def event_prefix(event_id: uuid.UUID) -> str:
    return f"big-events/{event_id}/"


def submission_prefix(event_id: uuid.UUID, team_id: uuid.UUID) -> str:
    return f"{event_prefix(event_id)}submissions/{team_id}/"


def case_prefix(event_id: uuid.UUID, case_id: uuid.UUID) -> str:
    return f"{event_prefix(event_id)}cases/{case_id}/"


def new_key(prefix: str, suffix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex}{suffix}"
