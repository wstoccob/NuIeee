import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.errors import ConflictError, InvalidError
from models.big_event import BigEvent, BigEventKind
from models.team import Team, TeamMember
from schemas.big_event import BigEventRead
from schemas.team import MemberInput, TeamRegistration
from services.big_events import count_teams


def name_key(name: str) -> str:
    return " ".join(name.split()).casefold()


async def get_team(session: AsyncSession, team_id: uuid.UUID) -> Team | None:
    return await session.get(Team, team_id)


async def register_team(session: AsyncSession, event: BigEvent, payload: TeamRegistration) -> Team:
    await _check_registration_allowed(session, event)
    _check_members(event, payload.members)
    await _check_members_not_registered(session, event, payload.members)

    team = Team(
        big_event_id=event.id,
        name=payload.team_name,
        name_key=name_key(payload.team_name),
        members=[
            TeamMember(position=index, **member.model_dump())
            for index, member in enumerate(payload.members)
        ],
    )
    session.add(team)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ConflictError("That team name is already taken for this event") from exc
    await session.refresh(team)
    return team


async def _check_registration_allowed(session: AsyncSession, event: BigEvent) -> None:
    if event.kind != BigEventKind.hackathon:
        raise ConflictError("This event does not take team registrations")
    if not BigEventRead.model_validate(event).registration_open:
        raise ConflictError("Registration for this event is closed")
    if event.capacity is not None and await count_teams(session, event.id) >= event.capacity:
        raise ConflictError("This event is full")


def _check_members(event: BigEvent, members: list[MemberInput]) -> None:
    if not event.min_team_size <= len(members) <= event.max_team_size:
        raise InvalidError(
            f"Teams must have between {event.min_team_size} and {event.max_team_size} members"
        )
    captains = sum(member.is_captain for member in members)
    if captains != 1:
        raise InvalidError("Choose exactly one team captain")

    emails = [member.email for member in members]
    duplicates = sorted({email for email in emails if emails.count(email) > 1})
    if duplicates:
        raise InvalidError(f"Each member needs their own email. Repeated: {', '.join(duplicates)}")


async def _check_members_not_registered(
    session: AsyncSession, event: BigEvent, members: list[MemberInput]
) -> None:
    emails = [member.email for member in members]
    stmt = (
        select(TeamMember.email)
        .join(Team, Team.id == TeamMember.team_id)
        .where(Team.big_event_id == event.id, func.lower(TeamMember.email).in_(emails))
    )
    taken = sorted(set(await session.scalars(stmt)))
    if taken:
        raise ConflictError(
            f"Already registered in another team for this event: {', '.join(taken)}"
        )


async def list_teams(session: AsyncSession, event_id: uuid.UUID) -> list[Team]:
    stmt = select(Team).where(Team.big_event_id == event_id).order_by(Team.created_at)
    return list(await session.scalars(stmt))


async def delete_team(session: AsyncSession, team: Team) -> None:
    await session.delete(team)
    await session.commit()
