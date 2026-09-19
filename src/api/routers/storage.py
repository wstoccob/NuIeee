from fastapi import APIRouter, Query, status

from api.deps import RequireAdmin
from schemas.storage import UploadTarget
from services import storage as storage_service

router = APIRouter(prefix="/storage", tags=["storage"], dependencies=[RequireAdmin])


@router.post("/upload-url", response_model=UploadTarget)
async def create_upload_url(
    filename: str = Query(min_length=1, max_length=255),
) -> UploadTarget:
    object_key = storage_service.build_object_key(filename)
    url = await storage_service.presigned_upload_url(object_key)
    return UploadTarget(
        upload_url=url,
        object_key=object_key,
        public_url=storage_service.public_url(object_key),
    )


@router.delete("/objects", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(key: str = Query(min_length=1, max_length=1024)) -> None:
    await storage_service.delete_object(key)
