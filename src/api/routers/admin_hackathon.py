import uuid

from fastapi import APIRouter, BackgroundTasks, status
from fastapi.responses import StreamingResponse

from api.deps import RequireAdmin, SessionDep
from core.errors import NotFoundError
from models.big_event import BigEvent
from models.case import Case
from models.team import Team
from schemas.big_event import BigEventAdminRead, BigEventWrite
from schemas.case import CaseRead, CaseWrite
from schemas.team import (
    AccessTokenIssued,
    AdminTeamRead,
    DownloadLink,
    PostUploadTarget,
    UploadConfirm,
    UploadRequest,
)
from services import big_events as big_event_service
from services import cases as case_service
from services import email, exports, notifications
from services import submissions as submission_service
from services import teams as team_service

router = APIRouter(prefix="/admin", tags=["admin: hackathons"], dependencies=[RequireAdmin])


async def _event(session: SessionDep, event_id: uuid.UUID) -> BigEvent:
    event = await big_event_service.get_big_event(session, event_id)
    if event is None:
        raise NotFoundError("Event not found")
    return event


async def _case(session: SessionDep, case_id: uuid.UUID) -> Case:
    case = await case_service.get_case(session, case_id)
    if case is None:
        raise NotFoundError("Case not found")
    return case


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


# --- cases ---------------------------------------------------------------------------


@router.get("/big-events/{event_id}/cases", response_model=list[CaseRead])
async def list_cases(event_id: uuid.UUID, session: SessionDep) -> list[CaseRead]:
    event = await _event(session, event_id)
    return [
        CaseRead.model_validate(case) for case in await case_service.list_cases(session, event.id)
    ]


@router.post(
    "/big-events/{event_id}/cases", response_model=CaseRead, status_code=status.HTTP_201_CREATED
)
async def create_case(event_id: uuid.UUID, payload: CaseWrite, session: SessionDep) -> CaseRead:
    case = await case_service.create_case(session, await _event(session, event_id), payload)
    return CaseRead.model_validate(case)


@router.put("/cases/{case_id}", response_model=CaseRead)
async def update_case(case_id: uuid.UUID, payload: CaseWrite, session: SessionDep) -> CaseRead:
    case = await case_service.update_case(session, await _case(session, case_id), payload)
    return CaseRead.model_validate(case)


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: uuid.UUID, session: SessionDep) -> None:
    await case_service.delete_case(session, await _case(session, case_id))


@router.post("/cases/{case_id}/attachment/upload-target", response_model=PostUploadTarget)
async def case_attachment_upload_target(
    case_id: uuid.UUID, payload: UploadRequest, session: SessionDep
) -> PostUploadTarget:
    case = await _case(session, case_id)
    form = await case_service.attachment_upload_form(case, payload.filename, payload.size_bytes)
    return PostUploadTarget(**form)


@router.put("/cases/{case_id}/attachment", response_model=CaseRead)
async def confirm_case_attachment(
    case_id: uuid.UUID, payload: UploadConfirm, session: SessionDep
) -> CaseRead:
    case = await case_service.attach_file(
        session, await _case(session, case_id), payload.object_key, payload.filename
    )
    return CaseRead.model_validate(case)


@router.delete("/cases/{case_id}/attachment", response_model=CaseRead)
async def remove_case_attachment(case_id: uuid.UUID, session: SessionDep) -> CaseRead:
    case = await case_service.remove_attachment(session, await _case(session, case_id))
    return CaseRead.model_validate(case)


@router.get("/cases/{case_id}/attachment", response_model=DownloadLink)
async def download_case_attachment(case_id: uuid.UUID, session: SessionDep) -> DownloadLink:
    case = await _case(session, case_id)
    return DownloadLink(url=await case_service.attachment_download_url(case))


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


@router.post("/teams/{team_id}/access-token", response_model=AccessTokenIssued)
async def rotate_team_link(
    team_id: uuid.UUID, session: SessionDep, background: BackgroundTasks
) -> AccessTokenIssued:
    team = await _team(session, team_id)
    event = await _event(session, team.big_event_id)
    token = await team_service.rotate_token(session, team)
    emailed = email.is_configured()
    if emailed:
        message = notifications.team_link_email(team, event, token, rotated=True)
        background.add_task(email.send, *message)
    return AccessTokenIssued(access_token=token, link_emailed=emailed)


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: uuid.UUID, session: SessionDep) -> None:
    await team_service.delete_team(session, await _team(session, team_id))


@router.get("/teams/{team_id}/submission", response_model=DownloadLink)
async def download_submission(team_id: uuid.UUID, session: SessionDep) -> DownloadLink:
    return DownloadLink(url=await submission_service.download_url(await _team(session, team_id)))
