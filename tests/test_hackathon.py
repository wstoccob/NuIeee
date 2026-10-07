"""Hackathon registration and the admin side: events, teams, CSV export."""

from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import func, select

from models.big_event import BigEvent, BigEventKind, BigEventStatus
from models.team import Team, TeamMember

NOW = datetime.now(UTC)
HOUR = timedelta(hours=1)


@pytest_asyncio.fixture
async def make_event(session):
    async def _make(slug: str = "hack-2026", **overrides) -> BigEvent:
        fields = {
            "slug": slug,
            "title": "IEEE Hackathon 2026",
            "kind": BigEventKind.hackathon,
            "status": BigEventStatus.published,
            "starts_at": NOW + 24 * HOUR,
            "ends_at": NOW + 48 * HOUR,
            "registration_opens_at": NOW - HOUR,
            "registration_closes_at": NOW + HOUR,
            "min_team_size": 2,
            "max_team_size": 3,
        }
        fields.update(overrides)
        event = BigEvent(**fields)
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    return _make


def member(name: str, email: str, captain: bool = False, **extra) -> dict:
    return {
        "fullName": name,
        "email": email,
        "nuId": extra.get("nu_id", "202012345"),
        "yearOfStudy": extra.get("year", "3"),
        "major": "Computer Science",
        "isCaptain": captain,
    }


def payload(team: str = "Byte Me", members: list[dict] | None = None, **overrides) -> dict:
    body = {
        "teamName": team,
        "consent": True,
        "members": members
        or [member("Aruzhan K", "aruzhan@nu.edu.kz", True), member("Dias M", "dias@nu.edu.kz")],
    }
    body.update(overrides)
    return body


async def register(client, slug: str = "hack-2026", **kwargs):
    return await client.post(f"/api/big-events/{slug}/teams", json=payload(**kwargs))


async def registered(client, slug: str = "hack-2026", **kwargs) -> str:
    res = await register(client, slug, **kwargs)
    assert res.status_code == 201, res.text
    return res.json()["teamId"]


# --- registration ------------------------------------------------------------------


async def test_registration_succeeds_and_returns_only_the_team_id(client, session, make_event):
    await make_event()
    res = await register(client)

    assert res.status_code == 201
    team = await session.scalar(select(Team))
    assert res.json() == {"teamId": str(team.id)}
    assert team.name == "Byte Me"
    assert [m.is_captain for m in team.members] == [True, False]


async def test_registration_closed_returns_409(client, make_event):
    await make_event(registration_opens_at=NOW - 3 * HOUR, registration_closes_at=NOW - HOUR)
    res = await register(client)
    assert res.status_code == 409
    assert "closed" in res.json()["detail"]


async def test_draft_event_is_not_registrable(client, make_event):
    await make_event(status=BigEventStatus.draft)
    assert (await register(client)).status_code == 404


async def test_conference_does_not_take_teams(client, make_event):
    await make_event(kind=BigEventKind.conference)
    assert (await register(client)).status_code == 409


@pytest.mark.parametrize("count", [1, 4])
async def test_team_size_is_enforced(client, make_event, count):
    await make_event()
    people = [member(f"Person {i}", f"p{i}@nu.edu.kz", captain=i == 0) for i in range(count)]
    res = await register(client, members=people)
    assert res.status_code == 422
    assert "between 2 and 3" in res.json()["detail"]


@pytest.mark.parametrize("captains", [0, 2])
async def test_exactly_one_captain_required(client, make_event, captains):
    await make_event()
    people = [member(f"P{i}", f"p{i}@nu.edu.kz", captain=i < captains) for i in range(2)]
    res = await register(client, members=people)
    assert res.status_code == 422
    assert "captain" in res.json()["detail"]


async def test_repeated_email_within_team_rejected(client, make_event):
    await make_event()
    people = [member("AA Person", "same@nu.edu.kz", True), member("BB Person", "SAME@nu.edu.kz")]
    res = await register(client, members=people)
    assert res.status_code == 422
    assert "same@nu.edu.kz" in res.json()["detail"]


async def test_team_name_is_unique_per_event_ignoring_case(client, make_event):
    await make_event()
    await registered(client)
    people = [member("CC Person", "c@nu.edu.kz", True), member("DD Person", "d@nu.edu.kz")]
    res = await register(client, team="  byte   ME ", members=people)
    assert res.status_code == 409
    assert "taken" in res.json()["detail"]


async def test_same_team_name_allowed_in_another_event(client, make_event):
    await make_event("hack-test")
    await make_event("hack-real")
    await registered(client, "hack-test")
    people = [member("CC Person", "c@nu.edu.kz", True), member("DD Person", "d@nu.edu.kz")]
    assert (await register(client, "hack-real", members=people)).status_code == 201


async def test_person_cannot_join_two_teams_in_one_event(client, make_event):
    await make_event()
    await registered(client)
    people = [member("New", "new@nu.edu.kz", True), member("Again", "dias@nu.edu.kz")]
    res = await register(client, team="Other Team", members=people)
    assert res.status_code == 409
    assert "dias@nu.edu.kz" in res.json()["detail"]


async def test_capacity_is_enforced(client, make_event):
    await make_event(capacity=1)
    await registered(client)
    people = [member("CC Person", "c@nu.edu.kz", True), member("DD Person", "d@nu.edu.kz")]
    res = await register(client, team="Late", members=people)
    assert res.status_code == 409
    assert "full" in res.json()["detail"]


async def test_consent_is_required(client, make_event):
    await make_event()
    assert (await register(client, consent=False)).status_code == 422


async def test_dash_nu_id_from_old_form_is_stored_as_empty(client, session, make_event):
    await make_event()
    people = [
        member("AA Person", "a@nu.edu.kz", True, nu_id="-"),
        member("BB Person", "b@x.com", nu_id=""),
    ]
    await registered(client, members=people)
    team = await session.scalar(select(Team))
    assert [m.nu_id for m in team.members] == [None, None]


async def test_no_iin_field_exists_anywhere():
    from schemas.team import MemberInput, MemberRead

    for model in (MemberInput, MemberRead):
        assert not any("iin" in name.lower() for name in model.model_fields)


# --- admin -------------------------------------------------------------------------


def event_body(slug: str = "test-hack", **overrides) -> dict:
    body = {
        "slug": slug,
        "title": "Test Hackathon",
        "kind": "hackathon",
        "status": "published",
        "startsAt": (NOW + 24 * HOUR).isoformat(),
        "endsAt": (NOW + 48 * HOUR).isoformat(),
        "registrationOpensAt": (NOW - HOUR).isoformat(),
        "registrationClosesAt": (NOW + HOUR).isoformat(),
        "minTeamSize": 4,
        "maxTeamSize": 5,
    }
    body.update(overrides)
    return body


async def test_admin_routes_require_admin(client):
    assert (await client.get("/api/admin/big-events")).status_code == 401


async def test_admin_creates_and_features_events(client, admin, auth_header):
    headers = auth_header(admin)
    first = await client.post(
        "/api/admin/big-events", json=event_body("test-hack", isFeatured=True), headers=headers
    )
    assert first.status_code == 201, first.text
    second = await client.post(
        "/api/admin/big-events", json=event_body("real-hack", isFeatured=True), headers=headers
    )
    assert second.status_code == 201

    events = {
        e["slug"]: e for e in (await client.get("/api/admin/big-events", headers=headers)).json()
    }
    assert events["real-hack"]["isFeatured"] is True
    assert events["test-hack"]["isFeatured"] is False, "featuring one event un-features the other"
    assert (await client.get("/api/big-events/featured")).json()["slug"] == "real-hack"


async def test_admin_event_validation(client, admin, auth_header):
    headers = auth_header(admin)
    bad_windows = event_body(registrationClosesAt=(NOW - 2 * HOUR).isoformat())
    assert (
        await client.post("/api/admin/big-events", json=bad_windows, headers=headers)
    ).status_code == 422
    too_small = event_body(minTeamSize=5, maxTeamSize=4)
    assert (
        await client.post("/api/admin/big-events", json=too_small, headers=headers)
    ).status_code == 422
    naive = event_body(startsAt="2026-10-05T10:00:00")
    assert (
        await client.post("/api/admin/big-events", json=naive, headers=headers)
    ).status_code == 422

    await client.post("/api/admin/big-events", json=event_body("dup"), headers=headers)
    res = await client.post("/api/admin/big-events", json=event_body("dup"), headers=headers)
    assert res.status_code == 409


async def test_admin_team_list_and_csv(client, admin, auth_header, make_event):
    headers = auth_header(admin)
    event = await make_event()
    people = [member("=HYPERLINK(evil)", "a@nu.edu.kz", True), member("Дана", "b@nu.edu.kz")]
    await registered(client, team="Команда", members=people)

    teams = (await client.get(f"/api/admin/big-events/{event.id}/teams", headers=headers)).json()
    assert teams[0]["name"] == "Команда"
    assert len(teams[0]["members"]) == 2
    assert set(teams[0]) == {"id", "name", "createdAt", "members"}

    csv = await client.get(f"/api/admin/big-events/{event.id}/teams.csv", headers=headers)
    assert csv.text.startswith("﻿"), "BOM so Excel reads Cyrillic correctly"
    assert "'=HYPERLINK(evil)" in csv.text, "formula injection must be neutralised"
    assert "Дана" in csv.text
    header = csv.text.lstrip("﻿").splitlines()[0]
    assert "Case" not in header and "Submi" not in header


async def test_admin_excel_export(client, admin, auth_header, make_event):
    import io
    import re
    import zipfile

    event = await make_event()
    people = [member("=HYPERLINK(evil)", "a@nu.edu.kz", True), member("Дана", "b@nu.edu.kz")]
    await registered(client, team="Команда", members=people)
    url = f"/api/admin/big-events/{event.id}/teams.xlsx"

    assert (await client.get(url)).status_code == 401
    res = await client.get(url, headers=auth_header(admin))
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert 'filename="hack-2026-teams.xlsx"' in res.headers["content-disposition"]

    book = zipfile.ZipFile(io.BytesIO(res.content))
    workbook = book.read("xl/workbook.xml").decode()
    assert 'name="Participants"' in workbook and 'name="Teams"' in workbook
    strings = book.read("xl/sharedStrings.xml").decode()
    assert "Команда" in strings and "Дана" in strings
    assert "=HYPERLINK(evil)" in strings, "participant text is stored as plain text"
    participants = book.read("xl/worksheets/sheet1.xml").decode()
    assert "<f>" not in participants, "no cell may hold a formula"
    assert len(re.findall(r"<row ", participants)) == 3, "header plus one row per member"
    teams_sheet = book.read("xl/worksheets/sheet2.xml").decode()
    assert len(re.findall(r"<row ", teams_sheet)) == 2, "header plus one row per team"


async def test_admin_deletes_a_team(client, session, admin, auth_header, make_event):
    headers = auth_header(admin)
    await make_event()
    team_id = await registered(client)

    assert (await client.delete(f"/api/admin/teams/{team_id}", headers=headers)).status_code == 204
    assert (await session.scalar(select(func.count(Team.id)))) == 0
    assert (await session.scalar(select(func.count(TeamMember.id)))) == 0
    assert (await client.delete(f"/api/admin/teams/{team_id}", headers=headers)).status_code == 404


# --- bot protection ----------------------------------------------------------------


async def test_honeypot_rejects_bots(client, make_event):
    await make_event()
    res = await register(client, website="http://spam.example")
    assert res.status_code == 422
    assert "verification" in res.json()["detail"]


async def test_turnstile_required_when_configured(client, make_event, monkeypatch):
    from services import turnstile

    await make_event()
    monkeypatch.setattr(turnstile.settings, "turnstile_secret", "secret")
    monkeypatch.setattr(
        turnstile,
        "_post",
        lambda token: {
            "success": token != "bad",
            "action": "other-form" if token == "wrong-action" else "hackathon-register",
            "hostname": "evil.example" if token == "wrong-host" else "ieee.nu",
        },
    )

    assert (await register(client)).status_code == 422, "missing token must fail"
    assert (await register(client, turnstileToken="bad")).status_code == 422
    assert (await register(client, turnstileToken="wrong-action")).status_code == 422, (
        "a token solved on a different form must not count"
    )
    assert (await register(client, turnstileToken="wrong-host")).status_code == 422, (
        "a token solved on another site with our public key must not count"
    )
    assert (await register(client, turnstileToken="good")).status_code == 201


async def test_turnstile_outage_does_not_block_registration(client, make_event, monkeypatch):
    import urllib.error

    from services import turnstile

    await make_event()
    monkeypatch.setattr(turnstile.settings, "turnstile_secret", "secret")

    def boom(token):
        raise urllib.error.URLError("cloudflare down")

    monkeypatch.setattr(turnstile, "_post", boom)
    assert (await register(client, turnstileToken="anything")).status_code == 201
