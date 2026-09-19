"""Events API, including regressions from the ASP.NET implementation:
missing 404s, and the detached-graph update that leaked orphaned photos."""

import uuid

PAYLOAD = {
    "title": "IEEE Speed Dating",
    "description": "Networking event",
    "startsAt": "2026-02-16T13:00:00+05:00",
    "photos": [
        {"photoUrl": "https://minio.ieee.nu/event-photos/a.jpg", "altText": "a"},
        {"photoUrl": "https://minio.ieee.nu/event-photos/b.jpg", "altText": "b"},
    ],
}


async def _create(client, auth_header, admin, **overrides):
    body = PAYLOAD | overrides
    return await client.post("/api/events", json=body, headers=auth_header(admin))


async def test_create_returns_201_and_camelcase_body(client, auth_header, admin):
    res = await _create(client, auth_header, admin)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "IEEE Speed Dating"
    assert body["startsAt"].startswith("2026-02-16")
    assert len(body["photos"]) == 2


async def test_has_registration_link_is_derived_not_stored(client, auth_header, admin):
    without = (await _create(client, auth_header, admin)).json()
    assert without["hasRegistrationLink"] is False

    with_link = (
        await _create(client, auth_header, admin, registrationLink="https://ieee.nu/reg")
    ).json()
    assert with_link["hasRegistrationLink"] is True


async def test_missing_event_returns_404_not_500(client):
    res = await client.get(f"/api/events/{uuid.uuid4()}")
    assert res.status_code == 404


async def test_delete_missing_event_returns_404_not_500(client, auth_header, admin):
    res = await client.delete(f"/api/events/{uuid.uuid4()}", headers=auth_header(admin))
    assert res.status_code == 404


async def test_update_removes_orphaned_photos(client, auth_header, admin, session):
    from sqlalchemy import func, select

    from models.event import EventPhoto

    created = (await _create(client, auth_header, admin)).json()
    assert await session.scalar(select(func.count()).select_from(EventPhoto)) == 2

    shrunk = PAYLOAD | {"photos": [PAYLOAD["photos"][0]]}
    res = await client.put(f"/api/events/{created['id']}", json=shrunk, headers=auth_header(admin))
    assert res.status_code == 200
    assert len(res.json()["photos"]) == 1

    remaining = await session.scalar(select(func.count()).select_from(EventPhoto))
    assert remaining == 1, "dropped photo must be deleted, not orphaned"


async def test_list_respects_limit(client, auth_header, admin):
    for i in range(3):
        await _create(client, auth_header, admin, title=f"Event {i}")

    res = await client.get("/api/events", params={"limit": 2})
    assert res.status_code == 200
    assert len(res.json()) == 2


async def test_write_requires_authentication(client):
    assert (await client.post("/api/events", json=PAYLOAD)).status_code == 401


async def test_reads_are_public(client):
    assert (await client.get("/api/events")).status_code == 200
