import hashlib
import secrets
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.errors import ConflictError, InvalidError, NotFoundError
from models.big_event import BigEvent, BigEventKind
from models.team import Team, TeamMember
from schemas.big_event import BigEventRead
from schemas.team import MemberInput, TeamRegistration
from services import storage
from services.big_events import count_teams
from services.cases import get_case
from services.uploads import submission_prefix


def _hash_token(token: str) -> str:
    # The token carries 256 bits of randomness, so a fast hash is enough: there is
    # nothing to brute-force. Argon2 is for low-entropy human passwords.
    return hashlib.sha256(token.encode()).hexdigest()


def _new_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, _hash_token(token)


def name_key(name: str) -> str:
    return " ".join(name.split()).casefold()


async def get_team_by_token(session: AsyncSession, token: str) -> Team | None:
    stmt = select(Team).where(Team.access_token_hash == _hash_token(token))
    return await session.scalar(stmt)


async def get_team(session: AsyncSession, team_id: uuid.UUID) -> Team | None:
    return await session.get(Team, team_id)


async def register_team(
    session: AsyncSession, event: BigEvent, payload: TeamRegistration
) -> tuple[Team, str]:
    """Create a team and return it with its one-time access token."""
    await _check_registration_allowed(session, event)
    _check_members(event, payload.members)
    await _check_members_not_registered(session, event, payload.members)

    token, token_hash = _new_token()
    team = Team(
        big_event_id=event.id,
        name=payload.team_name,
        name_key=name_key(payload.team_name),
        access_token_hash=token_hash,
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
    return team, token


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


async def choose_case(session: AsyncSession, team: Team, case_id: uuid.UUID) -> Team:
    event = await session.get(BigEvent, team.big_event_id)
    if not BigEventRead.model_validate(event).case_selection_open:
        raise ConflictError("Case selection is not open")
    case = await get_case(session, case_id)
    if case is None or case.big_event_id != team.big_event_id:
        raise NotFoundError("Case not found")
    team.case_id = case.id
    await session.commit()
    await session.refresh(team)
    return team


async def list_teams(session: AsyncSession, event_id: uuid.UUID) -> list[Team]:
    stmt = select(Team).where(Team.big_event_id == event_id).order_by(Team.created_at)
    return list(await session.scalars(stmt))


async def rotate_token(session: AsyncSession, team: Team) -> str:
    """Issue a new link for a team that lost theirs. The old link stops working."""
    token, token_hash = _new_token()
    team.access_token_hash = token_hash
    await session.commit()
    return token


async def delete_team(session: AsyncSession, team: Team) -> None:
    event_id, team_id = team.big_event_id, team.id
    await session.delete(team)
    await session.commit()
    await storage.delete_private_prefix(submission_prefix(event_id, team_id))
