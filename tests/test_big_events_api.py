from datetime import UTC, datetime, timedelta


async def test_featured_registration_open(client, create_big_event):
    now = datetime.now(UTC)
    await create_big_event(
        slug="hackathon-2026",
        status="published",
        is_featured=True,
        registration_opens_at=now - timedelta(days=1),
        registration_closes_at=now + timedelta(days=1),
    )

    response = await client.get("/api/big-events/featured")

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "hackathon-2026"
    assert body["registrationOpen"] is True


async def test_featured_registration_closed(client, create_big_event):
    now = datetime.now(UTC)
    await create_big_event(
        slug="hackathon-2026",
        status="published",
        is_featured=True,
        registration_opens_at=now - timedelta(days=10),
        registration_closes_at=now - timedelta(days=1),
    )

    response = await client.get("/api/big-events/featured")

    assert response.status_code == 200
    assert response.json()["registrationOpen"] is False


async def test_featured_none_returns_204(client):
    response = await client.get("/api/big-events/featured")

    assert response.status_code == 204
    assert response.content == b""


async def test_slug_draft_is_404(client, create_big_event):
    await create_big_event(slug="secret-event", status="draft")

    response = await client.get("/api/big-events/secret-event")

    assert response.status_code == 404


async def test_slug_published_returns_200(client, create_big_event):
    now = datetime.now(UTC)
    await create_big_event(
        slug="open-day",
        status="published",
        registration_opens_at=now - timedelta(days=1),
        registration_closes_at=now + timedelta(days=1),
    )

    response = await client.get("/api/big-events/open-day")

    assert response.status_code == 200
    assert response.json()["slug"] == "open-day"


async def test_slug_unknown_is_404(client):
    response = await client.get("/api/big-events/does-not-exist")

    assert response.status_code == 404
