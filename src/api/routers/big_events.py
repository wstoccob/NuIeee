from fastapi import APIRouter, Response, status

from api.deps import SessionDep
from core.errors import InvalidError, not_found
from models.big_event import BigEventStatus
from schemas.big_event import BigEventRead
from schemas.team import RegistrationResult, TeamRegistration
from services import big_events as big_event_service
from services import teams as team_service
from services import turnstile

router = APIRouter(prefix="/big-events", tags=["big-events"])


@router.get(
    "/featured",
    response_model=BigEventRead,
    responses={204: {"description": "No event is featured"}},
)
async def get_featured_big_event(session: SessionDep) -> BigEventRead | Response:
    event = await big_event_service.get_featured_big_event(session)
    if event is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return BigEventRead.model_validate(event)


@router.get("/{slug}", response_model=BigEventRead)
async def get_big_event_by_slug(slug: str, session: SessionDep) -> BigEventRead:
    event = await big_event_service.get_big_event_by_slug(session, slug)
    if event is None or event.status != BigEventStatus.published:
        raise not_found("Event")
    return BigEventRead.model_validate(event)


@router.post(
    "/{slug}/teams", response_model=RegistrationResult, status_code=status.HTTP_201_CREATED
)
async def register_team(
    slug: str, payload: TeamRegistration, session: SessionDep
) -> RegistrationResult:
    event = await big_event_service.get_big_event_by_slug(session, slug)
    if event is None or event.status != BigEventStatus.published:
        raise not_found("Event")
    # A real error rather than a fake success: browser autofill can occasionally fill
    # a hidden field, and a silently dropped human registration is worse than a bot.
    if payload.website or not await turnstile.verify(payload.turnstile_token):
        raise InvalidError("Please complete the verification and try again")
    team, token = await team_service.register_team(session, event, payload)
    return RegistrationResult(team_id=team.id, access_token=token)
