import uuid
from datetime import UTC, datetime, timedelta

import jwt

from core.config import settings
from models.user import Role


class TokenError(Exception):
    pass


def issue_access_token(user_id: uuid.UUID, username: str, role: Role) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role.value,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
