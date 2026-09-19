"""CORS must allow the production domains and this project's Vercel preview builds,
and must keep rejecting everything else."""

import importlib

import pytest
from httpx import ASGITransport, AsyncClient

PREVIEW = "https://nuieee-client-o74b6w7pc-wstoccobs-projects.vercel.app"


@pytest.fixture
def app_with_regex(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGIN_REGEX",
        r"^https://nuieee-client-[a-z0-9]+-wstoccobs-projects\.vercel\.app$",
    )
    import core.config
    import main

    importlib.reload(core.config)
    importlib.reload(main)
    yield main.app

    monkeypatch.delenv("CORS_ORIGIN_REGEX", raising=False)
    importlib.reload(core.config)
    importlib.reload(main)


async def _preflight(app, origin: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.options(
            "/api/events",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )


async def test_production_origin_allowed(app_with_regex):
    res = await _preflight(app_with_regex, "https://ieee.nu")
    assert res.headers.get("access-control-allow-origin") == "https://ieee.nu"


async def test_vercel_preview_origin_allowed(app_with_regex):
    res = await _preflight(app_with_regex, PREVIEW)
    assert res.headers.get("access-control-allow-origin") == PREVIEW


async def test_unrelated_origin_still_rejected(app_with_regex):
    res = await _preflight(app_with_regex, "https://evil.example.com")
    assert res.headers.get("access-control-allow-origin") is None


async def test_lookalike_vercel_origin_rejected(app_with_regex):
    res = await _preflight(
        app_with_regex, "https://nuieee-client-x-wstoccobs-projects.vercel.app.evil.com"
    )
    assert res.headers.get("access-control-allow-origin") is None
