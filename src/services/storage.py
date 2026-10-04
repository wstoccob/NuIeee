import asyncio
import uuid
from datetime import timedelta
from pathlib import PurePosixPath

from minio import Minio

from core.config import settings

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
