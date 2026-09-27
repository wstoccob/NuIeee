from fastapi import APIRouter, Response, status

from api.deps import SessionDep
from core.errors import not_found
from models.big_event import BigEventStatus
from schemas.big_event import BigEventRead
from services import big_events as big_event_service

router = APIRouter(prefix="/big-events", tags=["big-events"])


@router.get("/featured", response_model=None)
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
