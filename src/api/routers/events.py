import uuid

from fastapi import APIRouter, Query, status

from api.deps import RequireAdmin, SessionDep
from core.errors import not_found
from schemas.event import EventRead, EventWrite
from services import events as event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventRead])
async def list_events(
    session: SessionDep,
    limit: int | None = Query(default=None, ge=1, le=100),
) -> list[EventRead]:
    events = await event_service.list_events(session, limit)
    return [EventRead.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: uuid.UUID, session: SessionDep) -> EventRead:
    event = await event_service.get_event(session, event_id)
    if event is None:
        raise not_found("Event")
    return EventRead.model_validate(event)


@router.post(
    "", response_model=EventRead, status_code=status.HTTP_201_CREATED, dependencies=[RequireAdmin]
)
async def create_event(payload: EventWrite, session: SessionDep) -> EventRead:
    event = await event_service.create_event(session, payload)
    return EventRead.model_validate(event)


@router.put("/{event_id}", response_model=EventRead, dependencies=[RequireAdmin])
async def update_event(event_id: uuid.UUID, payload: EventWrite, session: SessionDep) -> EventRead:
    event = await event_service.get_event(session, event_id)
    if event is None:
        raise not_found("Event")
    updated = await event_service.replace_event(session, event, payload)
    return EventRead.model_validate(updated)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAdmin])
async def delete_event(event_id: uuid.UUID, session: SessionDep) -> None:
    event = await event_service.get_event(session, event_id)
    if event is None:
        raise not_found("Event")
    await event_service.delete_event(session, event)
