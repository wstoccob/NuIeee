import os
from functools import cached_property

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ENV_FILE="" disables .env loading; the test suite relies on that so a developer's
    # local .env cannot override the values the tests assert against.
    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ".env") or None, extra="ignore"
    )

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

    # Hackathon submissions and case briefs. Must NOT be the public photo bucket:
    # anything there is readable by anyone who can guess the URL.
    minio_private_bucket: str = "hackathon-files"
    private_upload_ttl_seconds: int = 900
    private_download_ttl_seconds: int = 600
    submission_max_bytes: int = 50 * 1024 * 1024
    case_attachment_max_bytes: int = 50 * 1024 * 1024

    # Outgoing mail over plain SMTP, so the provider (Gmail app password, Resend, ...) is
    # configuration only. Unset host or sender means emails are skipped.
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    mail_from: str | None = None
    # Public site used to build links inside emails.
    public_site_url: str = "https://ieee.nu"
    # Emails are read on phones with no notion of the sender's zone, so state one.
    mail_time_zone: str = "Asia/Almaty"

    # Cloudflare Turnstile. Unset means registration runs without a bot check.
    turnstile_secret: str | None = None
    turnstile_action: str = "hackathon-register"
    # Empty list skips the hostname check (local testing with Cloudflare's test keys).
    turnstile_hostnames: list[str] = ["ieee.nu", "www.ieee.nu"]

    @cached_property
    def dsn(self) -> str:
        return str(self.database_url)


settings = Settings()
