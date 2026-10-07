import uuid

from fastapi import APIRouter, status
from fastapi.responses import Response, StreamingResponse

from api.deps import RequireAdmin, SessionDep
from core.errors import NotFoundError
from models.big_event import BigEvent
from models.team import Team
from schemas.big_event import BigEventAdminRead, BigEventWrite
from schemas.team import AdminTeamRead
from services import big_events as big_event_service
from services import exports
from services import teams as team_service

router = APIRouter(prefix="/admin", tags=["admin: hackathons"], dependencies=[RequireAdmin])


async def _event(session: SessionDep, event_id: uuid.UUID) -> BigEvent:
    event = await big_event_service.get_big_event(session, event_id)
    if event is None:
        raise NotFoundError("Event not found")
    return event


async def _team(session: SessionDep, team_id: uuid.UUID) -> Team:
    team = await team_service.get_team(session, team_id)
    if team is None:
        raise NotFoundError("Team not found")
    return team


def _admin_read(event: BigEvent, team_count: int) -> BigEventAdminRead:
    return BigEventAdminRead.model_validate(event).model_copy(update={"team_count": team_count})


# --- events --------------------------------------------------------------------------


@router.get("/big-events", response_model=list[BigEventAdminRead])
async def list_events(session: SessionDep) -> list[BigEventAdminRead]:
    rows = await big_event_service.list_big_events(session)
    return [_admin_read(event, count) for event, count in rows]


@router.post("/big-events", response_model=BigEventAdminRead, status_code=status.HTTP_201_CREATED)
async def create_event(payload: BigEventWrite, session: SessionDep) -> BigEventAdminRead:
    event = await big_event_service.create_big_event(session, payload)
    return _admin_read(event, 0)


@router.get("/big-events/{event_id}", response_model=BigEventAdminRead)
async def get_event(event_id: uuid.UUID, session: SessionDep) -> BigEventAdminRead:
    event = await _event(session, event_id)
    return _admin_read(event, await big_event_service.count_teams(session, event.id))


@router.put("/big-events/{event_id}", response_model=BigEventAdminRead)
async def update_event(
    event_id: uuid.UUID, payload: BigEventWrite, session: SessionDep
) -> BigEventAdminRead:
    event = await big_event_service.update_big_event(
        session, await _event(session, event_id), payload
    )
    return _admin_read(event, await big_event_service.count_teams(session, event.id))


@router.delete("/big-events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: uuid.UUID, session: SessionDep) -> None:
    await big_event_service.delete_big_event(session, await _event(session, event_id))


# --- teams ---------------------------------------------------------------------------


@router.get("/big-events/{event_id}/teams", response_model=list[AdminTeamRead])
async def list_teams(event_id: uuid.UUID, session: SessionDep) -> list[AdminTeamRead]:
    event = await _event(session, event_id)
    return [
        AdminTeamRead.model_validate(t) for t in await team_service.list_teams(session, event.id)
    ]


@router.get("/big-events/{event_id}/teams.csv")
async def export_teams(event_id: uuid.UUID, session: SessionDep) -> StreamingResponse:
    event = await _event(session, event_id)
    teams = await team_service.list_teams(session, event.id)
    return StreamingResponse(
        exports.teams_csv(teams),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{event.slug}-teams.csv"'},
    )


@router.get("/big-events/{event_id}/teams.xlsx")
async def export_teams_excel(event_id: uuid.UUID, session: SessionDep) -> Response:
    event = await _event(session, event_id)
    teams = await team_service.list_teams(session, event.id)
    return Response(
        exports.teams_xlsx(teams),
        media_type=exports.XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{event.slug}-teams.xlsx"'},
    )


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: uuid.UUID, session: SessionDep) -> None:
    await team_service.delete_team(session, await _team(session, team_id))
