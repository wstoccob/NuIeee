from schemas.base import CamelModel


class UploadTarget(CamelModel):
    upload_url: str
    object_key: str
    public_url: str
