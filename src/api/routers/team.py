import uuid

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentTeam, SessionDep
from core.config import settings
from core.errors import NotFoundError
from models.team import Team
from schemas.big_event import BigEventRead
from schemas.case import CaseRead
from schemas.team import (
    CaseChoice,
    DownloadLink,
    MemberRead,
    PostUploadTarget,
    SubmissionRead,
    TeamDashboard,
    UploadConfirm,
    UploadRequest,
)
from services import big_events as big_event_service
from services import cases as case_service
from services import submissions as submission_service
from services import teams as team_service

router = APIRouter(prefix="/team", tags=["team"])


async def build_dashboard(session: AsyncSession, team: Team) -> TeamDashboard:
    event = BigEventRead.model_validate(
        await big_event_service.get_big_event(session, team.big_event_id)
    )
    cases = await case_service.list_cases(session, event.id) if event.cases_visible else []
    return TeamDashboard(
        id=team.id,
        name=team.name,
        created_at=team.created_at,
        members=[MemberRead.model_validate(member) for member in team.members],
        event=event,
        case=CaseRead.model_validate(team.case) if team.case else None,
        cases=[CaseRead.model_validate(case) for case in cases],
        submission=SubmissionRead.model_validate(team.submission) if team.submission else None,
        submission_max_bytes=settings.submission_max_bytes,
    )


@router.get("", response_model=TeamDashboard)
async def get_dashboard(team: CurrentTeam, session: SessionDep) -> TeamDashboard:
    return await build_dashboard(session, team)


@router.put("/case", response_model=TeamDashboard)
async def choose_case(payload: CaseChoice, team: CurrentTeam, session: SessionDep) -> TeamDashboard:
    team = await team_service.choose_case(session, team, payload.case_id)
    return await build_dashboard(session, team)


@router.get("/cases/{case_id}/attachment", response_model=DownloadLink)
async def case_attachment(
    case_id: uuid.UUID, team: CurrentTeam, session: SessionDep
) -> DownloadLink:
    event = BigEventRead.model_validate(
        await big_event_service.get_big_event(session, team.big_event_id)
    )
    case = await case_service.get_case(session, case_id)
    if case is None or case.big_event_id != team.big_event_id or not event.cases_visible:
        raise NotFoundError("Case not found")
    return DownloadLink(url=await case_service.attachment_download_url(case))


@router.post("/submission/upload-target", response_model=PostUploadTarget)
async def submission_upload_target(
    payload: UploadRequest, team: CurrentTeam, session: SessionDep
) -> PostUploadTarget:
    form = await submission_service.upload_form(session, team, payload.filename, payload.size_bytes)
    return PostUploadTarget(**form)


@router.put("/submission", response_model=TeamDashboard)
async def confirm_submission(
    payload: UploadConfirm, team: CurrentTeam, session: SessionDep
) -> TeamDashboard:
    team = await submission_service.confirm(session, team, payload.object_key, payload.filename)
    return await build_dashboard(session, team)
