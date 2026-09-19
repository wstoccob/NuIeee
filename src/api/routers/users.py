import uuid

from fastapi import APIRouter, status

from api.deps import CurrentUser, RequireSuperAdmin, SessionDep
from core.errors import conflict, forbidden, not_found
from schemas.user import UserCreate, UserRead
from services import users as user_service

router = APIRouter(prefix="/users", tags=["users"], dependencies=[RequireSuperAdmin])


@router.get("", response_model=list[UserRead])
async def list_users(session: SessionDep) -> list[UserRead]:
    users = await user_service.list_users(session)
    return [UserRead.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, session: SessionDep) -> UserRead:
    user = await user_service.get_user(session, user_id)
    if user is None:
        raise not_found("User")
    return UserRead.model_validate(user)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: SessionDep) -> UserRead:
    if await user_service.get_by_username(session, payload.username) is not None:
        raise conflict(f"Username '{payload.username}' is already taken")
    user = await user_service.create_user(session, payload)
    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, session: SessionDep, actor: CurrentUser) -> None:
    user = await user_service.get_user(session, user_id)
    if user is None:
        raise not_found("User")
    if user.id == actor.id:
        raise forbidden("You cannot delete your own account")

    existing = await user_service.list_users(session)
    if user_service.is_last_superadmin(existing, user):
        raise forbidden("Cannot delete the last superadmin")

    await user_service.delete_user(session, user)
