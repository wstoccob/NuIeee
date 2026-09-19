from functools import cached_property

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: PostgresDsn
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 180

    cors_origins: list[str] = ["https://ieee.nu", "https://www.ieee.nu"]
    # Vercel preview deployments get a generated hostname per build, so they
    # cannot be listed individually.
    cors_origin_regex: str | None = None

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "event-photos"
    minio_secure: bool = True
    minio_public_base_url: str = "https://minio.ieee.nu"
    presigned_url_ttl_seconds: int = 3600

    @cached_property
    def dsn(self) -> str:
        return str(self.database_url)


settings = Settings()
