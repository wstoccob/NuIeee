import asyncio
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from core.config import settings

logger = logging.getLogger(__name__)

_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def _post(token: str) -> dict:
    data = urllib.parse.urlencode({"secret": settings.turnstile_secret, "response": token})
    request = urllib.request.Request(_VERIFY_URL, data=data.encode(), method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


def _accepted(result: dict) -> bool:
    if not result.get("success"):
        return False
    # The site key is public, so a token solved on someone else's page would otherwise
    # pass. Pinning action and hostname ties the token to our registration form.
    if result.get("action") != settings.turnstile_action:
        return False
    allowed = settings.turnstile_hostnames
    return not allowed or result.get("hostname") in allowed


async def verify(token: str | None) -> bool:
    """Check a Cloudflare Turnstile token. Always passes when no secret is configured.

    Fails open if Cloudflare itself is unreachable: an outage on their side must not
    stop real participants from registering, and a bot cannot cause one.
    """
    if not settings.turnstile_secret:
        return True
    if not token:
        return False
    try:
        result = await asyncio.to_thread(_post, token)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        logger.exception("turnstile verification unavailable, allowing registration")
        return True
    accepted = _accepted(result)
    if not accepted:
        logger.info(
            "turnstile rejected: success=%s action=%s hostname=%s errors=%s",
            result.get("success"),
            result.get("action"),
            result.get("hostname"),
            result.get("error-codes"),
        )
    return accepted
