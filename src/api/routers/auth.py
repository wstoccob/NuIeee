from fastapi import APIRouter

from api.deps import CurrentUser, SessionDep
from core.config import settings
from core.errors import unauthorized
from core.security.jwt import issue_access_token
from core.security.passwords import verify_password
from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserRead
from services import users as user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: SessionDep) -> TokenResponse:
    user = await user_service.get_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise unauthorized()

    token = issue_access_token(user.id, user.username, user.role)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_ttl_minutes * 60,
    )


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
