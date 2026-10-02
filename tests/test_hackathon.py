"""Hackathon registration, case selection, submissions and the admin side.

Storage is faked throughout; see the fake_storage fixture in conftest.py.
"""

from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import select

from models.big_event import BigEvent, BigEventKind, BigEventStatus
from models.case import Case
from models.team import Team

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


@pytest_asyncio.fixture
async def make_case(session):
    async def _make(
        event: BigEvent, company: str = "Kaspi", title: str = "Fraud detection"
    ) -> Case:
        case = Case(big_event_id=event.id, company=company, title=title, description="")
        session.add(case)
        await session.commit()
        await session.refresh(case)
        return case

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


async def registered_token(client, slug: str = "hack-2026", **kwargs) -> str:
    res = await register(client, slug, **kwargs)
    assert res.status_code == 201, res.text
    return res.json()["accessToken"]


def team_header(token: str) -> dict:
    return {"X-Team-Token": token}


# --- registration ------------------------------------------------------------------


async def test_registration_succeeds_and_returns_token_once(client, session, make_event):
    await make_event()
    res = await register(client)

    assert res.status_code == 201
    token = res.json()["accessToken"]
    assert len(token) >= 40

    team = await session.scalar(select(Team))
    assert team.name == "Byte Me"
    assert token not in team.access_token_hash, "only a hash of the token may be stored"
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
    await registered_token(client)
    people = [member("CC Person", "c@nu.edu.kz", True), member("DD Person", "d@nu.edu.kz")]
    res = await register(client, team="  byte   ME ", members=people)
    assert res.status_code == 409
    assert "taken" in res.json()["detail"]


async def test_same_team_name_allowed_in_another_event(client, make_event):
    await make_event("hack-test")
    await make_event("hack-real")
    await registered_token(client, "hack-test")
    people = [member("CC Person", "c@nu.edu.kz", True), member("DD Person", "d@nu.edu.kz")]
    assert (await register(client, "hack-real", members=people)).status_code == 201


async def test_person_cannot_join_two_teams_in_one_event(client, make_event):
    await make_event()
    await registered_token(client)
    people = [member("New", "new@nu.edu.kz", True), member("Again", "dias@nu.edu.kz")]
    res = await register(client, team="Other Team", members=people)
    assert res.status_code == 409
    assert "dias@nu.edu.kz" in res.json()["detail"]


async def test_capacity_is_enforced(client, make_event):
    await make_event(capacity=1)
    await registered_token(client)
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
    await registered_token(client, members=people)
    team = await session.scalar(select(Team))
    assert [m.nu_id for m in team.members] == [None, None]


async def test_no_iin_field_exists_anywhere():
    from schemas.team import MemberInput, MemberRead

    for model in (MemberInput, MemberRead):
        assert not any("iin" in name.lower() for name in model.model_fields)


# --- team dashboard and case selection ---------------------------------------------


async def test_team_endpoints_require_a_valid_link(client, make_event):
    await make_event()
    assert (await client.get("/api/team")).status_code == 401
    assert (await client.get("/api/team", headers=team_header("nope"))).status_code == 401


async def test_cases_hidden_until_case_selection_opens(client, make_event, make_case):
    event = await make_event(case_selection_opens_at=NOW + HOUR)
    await make_case(event)
    token = await registered_token(client)

    body = (await client.get("/api/team", headers=team_header(token))).json()
    assert body["name"] == "Byte Me"
    assert body["event"]["casesVisible"] is False
    assert body["cases"] == []


async def test_team_picks_a_case_once_selection_opens(client, make_event, make_case):
    event = await make_event(case_selection_opens_at=NOW - HOUR)
    case = await make_case(event)
    token = await registered_token(client)

    res = await client.put(
        "/api/team/case", json={"caseId": str(case.id)}, headers=team_header(token)
    )
    assert res.status_code == 200
    assert res.json()["case"]["company"] == "Kaspi"
    assert len(res.json()["cases"]) == 1


async def test_case_selection_closed_returns_409(client, make_event, make_case):
    event = await make_event(case_selection_opens_at=NOW + HOUR)
    case = await make_case(event)
    token = await registered_token(client)
    res = await client.put(
        "/api/team/case", json={"caseId": str(case.id)}, headers=team_header(token)
    )
    assert res.status_code == 409


async def test_cannot_pick_another_events_case(client, make_event, make_case):
    await make_event(case_selection_opens_at=NOW - HOUR)
    other = await make_event("other-hack", case_selection_opens_at=NOW - HOUR)
    foreign = await make_case(other)
    token = await registered_token(client)
    res = await client.put(
        "/api/team/case", json={"caseId": str(foreign.id)}, headers=team_header(token)
    )
    assert res.status_code == 404


# --- submissions ---------------------------------------------------------------------


async def _team_with_case(client, make_event, make_case, **event_fields) -> str:
    fields = {
        "case_selection_opens_at": NOW - 2 * HOUR,
        "submissions_open_at": NOW - HOUR,
        "submissions_close_at": NOW + HOUR,
    }
    fields.update(event_fields)
    event = await make_event(**fields)
    case = await make_case(event)
    token = await registered_token(client)
    await client.put("/api/team/case", json={"caseId": str(case.id)}, headers=team_header(token))
    return token


async def _upload_target(client, token: str, filename: str = "deck.pdf", size: int = 2048):
    return await client.post(
        "/api/team/submission/upload-target",
        json={"filename": filename, "sizeBytes": size},
        headers=team_header(token),
    )


async def test_submission_requires_a_chosen_case(client, make_event, fake_storage):
    await make_event(submissions_open_at=NOW - HOUR, submissions_close_at=NOW + HOUR)
    token = await registered_token(client)
    res = await _upload_target(client, token)
    assert res.status_code == 409
    assert "case" in res.json()["detail"]


async def test_submission_window_is_enforced(client, make_event, make_case, fake_storage):
    token = await _team_with_case(
        client,
        make_event,
        make_case,
        submissions_open_at=NOW + HOUR,
        submissions_close_at=NOW + 2 * HOUR,
    )
    assert (await _upload_target(client, token)).status_code == 409


@pytest.mark.parametrize(
    ("filename", "size"), [("deck.key", 100), ("notes.docx", 100), ("deck.pdf", 60 * 1024 * 1024)]
)
async def test_submission_type_and_size_rules(
    client, make_event, make_case, fake_storage, filename, size
):
    token = await _team_with_case(client, make_event, make_case)
    assert (await _upload_target(client, token, filename, size)).status_code == 422


async def test_upload_target_derives_content_type_from_extension(
    client, make_event, make_case, fake_storage
):
    token = await _team_with_case(client, make_event, make_case)
    res = await _upload_target(client, token, "Final Deck.PPTX")
    assert res.status_code == 200
    body = res.json()
    assert body["url"] == "https://storage.test/hackathon-files"
    assert body["fields"]["Content-Type"].endswith("presentationml.presentation")
    assert body["objectKey"].endswith(".pptx")
    assert body["fields"]["key"] == body["objectKey"]


async def test_full_submission_flow_and_resubmission(client, make_event, make_case, fake_storage):
    token = await _team_with_case(client, make_event, make_case)

    first = (await _upload_target(client, token)).json()
    fake_storage.put(first["objectKey"], size=3000)
    res = await client.put(
        "/api/team/submission",
        json={"objectKey": first["objectKey"], "filename": "deck.pdf"},
        headers=team_header(token),
    )
    assert res.status_code == 200
    assert res.json()["submission"]["sizeBytes"] == 3000

    second = (await _upload_target(client, token)).json()
    fake_storage.put(second["objectKey"], size=4000)
    res = await client.put(
        "/api/team/submission",
        json={"objectKey": second["objectKey"], "filename": "deck-v2.pdf"},
        headers=team_header(token),
    )
    assert res.json()["submission"]["originalFilename"] == "deck-v2.pdf"
    assert first["objectKey"] in fake_storage.deleted, "the replaced file must be removed"


async def test_cannot_confirm_another_teams_upload(client, make_event, make_case, fake_storage):
    token = await _team_with_case(client, make_event, make_case)
    res = await client.put(
        "/api/team/submission",
        json={"objectKey": "big-events/x/submissions/y/stolen.pdf", "filename": "x.pdf"},
        headers=team_header(token),
    )
    assert res.status_code == 422


async def test_confirm_without_uploaded_file_returns_404(
    client, make_event, make_case, fake_storage
):
    token = await _team_with_case(client, make_event, make_case)
    target = (await _upload_target(client, token)).json()
    res = await client.put(
        "/api/team/submission",
        json={"objectKey": target["objectKey"], "filename": "deck.pdf"},
        headers=team_header(token),
    )
    assert res.status_code == 404


async def test_upload_finished_after_deadline_is_rejected(
    client, make_event, make_case, fake_storage
):
    token = await _team_with_case(client, make_event, make_case)
    target = (await _upload_target(client, token)).json()
    fake_storage.put(target["objectKey"], uploaded_at=NOW + 3 * HOUR)
    res = await client.put(
        "/api/team/submission",
        json={"objectKey": target["objectKey"], "filename": "deck.pdf"},
        headers=team_header(token),
    )
    assert res.status_code == 409


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
    one_sided = event_body(submissionsOpenAt=NOW.isoformat())
    assert (
        await client.post("/api/admin/big-events", json=one_sided, headers=headers)
    ).status_code == 422
    naive = event_body(startsAt="2026-10-05T10:00:00")
    assert (
        await client.post("/api/admin/big-events", json=naive, headers=headers)
    ).status_code == 422

    await client.post("/api/admin/big-events", json=event_body("dup"), headers=headers)
    res = await client.post("/api/admin/big-events", json=event_body("dup"), headers=headers)
    assert res.status_code == 409


async def test_admin_manages_cases(client, admin, auth_header, make_event):
    headers = auth_header(admin)
    event = await make_event()
    created = await client.post(
        f"/api/admin/big-events/{event.id}/cases",
        json={"company": "Halyk", "title": "Credit scoring", "description": "Build it"},
        headers=headers,
    )
    assert created.status_code == 201
    case_id = created.json()["id"]

    updated = await client.put(
        f"/api/admin/cases/{case_id}",
        json={"company": "Halyk Bank", "title": "Credit scoring", "sortOrder": 2},
        headers=headers,
    )
    assert updated.json()["company"] == "Halyk Bank"
    assert (await client.delete(f"/api/admin/cases/{case_id}", headers=headers)).status_code == 204
    listed = await client.get(f"/api/admin/big-events/{event.id}/cases", headers=headers)
    assert listed.json() == []


async def test_admin_case_attachment_flow(
    client, admin, auth_header, make_event, make_case, fake_storage
):
    headers = auth_header(admin)
    event = await make_event(case_selection_opens_at=NOW - HOUR)
    case = await make_case(event)

    target = await client.post(
        f"/api/admin/cases/{case.id}/attachment/upload-target",
        json={"filename": "brief.pdf", "sizeBytes": 500},
        headers=headers,
    )
    key = target.json()["objectKey"]
    fake_storage.put(key)
    res = await client.put(
        f"/api/admin/cases/{case.id}/attachment",
        json={"objectKey": key, "filename": "Kaspi brief.pdf"},
        headers=headers,
    )
    assert res.json()["hasAttachment"] is True

    token = await registered_token(client)
    link = await client.get(f"/api/team/cases/{case.id}/attachment", headers=team_header(token))
    assert link.status_code == 200
    assert key in link.json()["url"]


async def test_admin_team_list_csv_and_link_rotation(client, admin, auth_header, make_event):
    headers = auth_header(admin)
    event = await make_event()
    people = [member("=HYPERLINK(evil)", "a@nu.edu.kz", True), member("Дана", "b@nu.edu.kz")]
    old_token = await registered_token(client, team="Команда", members=people)

    teams = (await client.get(f"/api/admin/big-events/{event.id}/teams", headers=headers)).json()
    assert teams[0]["name"] == "Команда"
    assert len(teams[0]["members"]) == 2

    csv = await client.get(f"/api/admin/big-events/{event.id}/teams.csv", headers=headers)
    assert csv.text.startswith("﻿"), "BOM so Excel reads Cyrillic correctly"
    assert "'=HYPERLINK(evil)" in csv.text, "formula injection must be neutralised"
    assert "Дана" in csv.text

    rotated = await client.post(f"/api/admin/teams/{teams[0]['id']}/access-token", headers=headers)
    new_token = rotated.json()["accessToken"]
    assert (await client.get("/api/team", headers=team_header(old_token))).status_code == 401
    assert (await client.get("/api/team", headers=team_header(new_token))).status_code == 200


async def test_deleting_an_event_removes_its_files(
    client, admin, auth_header, make_event, fake_storage
):
    headers = auth_header(admin)
    event = await make_event()
    fake_storage.put(f"big-events/{event.id}/submissions/t/deck.pdf")
    fake_storage.put("big-events/someone-else/submissions/t/keep.pdf")

    assert (
        await client.delete(f"/api/admin/big-events/{event.id}", headers=headers)
    ).status_code == 204
    assert list(fake_storage.objects) == ["big-events/someone-else/submissions/t/keep.pdf"]


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
    monkeypatch.setattr(turnstile, "_post", lambda token: {"success": token == "good"})

    assert (await register(client)).status_code == 422, "missing token must fail"
    assert (await register(client, turnstileToken="bad")).status_code == 422
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
