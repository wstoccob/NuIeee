import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from core.errors import forbidden, unauthorized
from core.security.jwt import TokenError, decode_access_token
from models.user import Role, User, role_satisfies
from services import users as user_service

SessionDep = Annotated[AsyncSession, Depends(get_session)]
_bearer = HTTPBearer(auto_error=False)


async def current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise unauthorized("Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError as exc:
        raise unauthorized("Invalid or expired token") from exc

    user = await user_service.get_user(session, uuid.UUID(payload["sub"]))
    if user is None:
        raise unauthorized("User no longer exists")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_role(minimum: Role):
    async def guard(user: CurrentUser) -> User:
        if not role_satisfies(user.role, minimum):
            raise forbidden()
        return user

    return guard


RequireAdmin = Depends(require_role(Role.ADMIN))
RequireSuperAdmin = Depends(require_role(Role.SUPERADMIN))
