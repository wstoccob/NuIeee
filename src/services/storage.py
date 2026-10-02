import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import PurePosixPath
from urllib.parse import quote

from minio import Minio
from minio.datatypes import PostPolicy
from minio.error import S3Error

from core.clock import utcnow
from core.config import settings

logger = logging.getLogger(__name__)

_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure,
)


def build_object_key(filename: str) -> str:
    """Generate a collision-free, URL-safe object key.

    Live data contains keys with spaces and Cyrillic (e.g. 'Z30_1633-Улучшено.jpg'),
    which break when interpolated into a URL path. New uploads get a UUID stem and
    keep only the original suffix.
    """
    suffix = PurePosixPath(filename).suffix.lower()
    return f"{uuid.uuid4().hex}{suffix}"


def public_url(object_key: str) -> str:
    return f"{settings.minio_public_base_url.rstrip('/')}/{settings.minio_bucket}/{object_key}"


async def presigned_upload_url(object_key: str) -> str:
    return await asyncio.to_thread(
        _client.presigned_put_object,
        settings.minio_bucket,
        object_key,
        expires=timedelta(seconds=settings.presigned_url_ttl_seconds),
    )


async def delete_object(object_key: str) -> None:
    await asyncio.to_thread(_client.remove_object, settings.minio_bucket, object_key)


# --- private bucket: hackathon submissions and case briefs -------------------------

_private_bucket_ready = False


@dataclass(frozen=True)
class StoredObject:
    size_bytes: int
    content_type: str
    last_modified: datetime


def _ensure_private_bucket() -> None:
    global _private_bucket_ready
    if _private_bucket_ready:
        return
    bucket = settings.minio_private_bucket
    if not _client.bucket_exists(bucket):
        # New MinIO buckets are private by default, which is exactly what we want.
        _client.make_bucket(bucket)
    _private_bucket_ready = True


def _post_policy_form(object_key: str, content_type: str, max_bytes: int) -> dict[str, str]:
    _ensure_private_bucket()
    expires = utcnow() + timedelta(seconds=settings.private_upload_ttl_seconds)
    policy = PostPolicy(settings.minio_private_bucket, expires)
    policy.add_equals_condition("key", object_key)
    policy.add_equals_condition("Content-Type", content_type)
    policy.add_content_length_range_condition(1, max_bytes)
    form = _client.presigned_post_policy(policy)
    # The signer returns only signature fields; the conditioned values must be sent too.
    return {**form, "key": object_key, "Content-Type": content_type}


def private_bucket_url() -> str:
    scheme = "https" if settings.minio_secure else "http"
    return f"{scheme}://{settings.minio_endpoint}/{settings.minio_private_bucket}"


async def private_upload_form(object_key: str, content_type: str, max_bytes: int) -> dict:
    """Presigned POST whose size and type limits are enforced by storage, not the browser."""
    return await asyncio.to_thread(_post_policy_form, object_key, content_type, max_bytes)


def _stat(object_key: str) -> StoredObject | None:
    try:
        info = _client.stat_object(settings.minio_private_bucket, object_key)
    except S3Error as exc:
        if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            return None
        raise
    return StoredObject(info.size, info.content_type or "", info.last_modified)


async def stat_private(object_key: str) -> StoredObject | None:
    return await asyncio.to_thread(_stat, object_key)


def content_disposition(filename: str) -> str:
    """Attachment header that keeps non-ASCII names (team names are often Cyrillic)."""
    fallback = filename.encode("ascii", "ignore").decode() or "download"
    fallback = fallback.replace('"', "")
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename)}"


async def private_download_url(object_key: str, download_name: str) -> str:
    return await asyncio.to_thread(
        _client.presigned_get_object,
        settings.minio_private_bucket,
        object_key,
        expires=timedelta(seconds=settings.private_download_ttl_seconds),
        response_headers={"response-content-disposition": content_disposition(download_name)},
    )


async def delete_private(object_key: str) -> None:
    """Best effort: a leftover file is cheaper than a failed request."""
    try:
        await asyncio.to_thread(_client.remove_object, settings.minio_private_bucket, object_key)
    except Exception:
        logger.exception("could not delete private object %s", object_key)


def _delete_prefix(prefix: str) -> int:
    bucket = settings.minio_private_bucket
    if not _client.bucket_exists(bucket):
        return 0
    removed = 0
    for obj in _client.list_objects(bucket, prefix=prefix, recursive=True):
        _client.remove_object(bucket, obj.object_name)
        removed += 1
    return removed


async def delete_private_prefix(prefix: str) -> None:
    try:
        removed = await asyncio.to_thread(_delete_prefix, prefix)
        logger.info("removed %d private objects under %s", removed, prefix)
    except Exception:
        logger.exception("could not clean up private objects under %s", prefix)
