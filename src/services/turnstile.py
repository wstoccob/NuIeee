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
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode())


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
    if not result.get("success"):
        logger.info("turnstile rejected a registration: %s", result.get("error-codes"))
    return bool(result.get("success"))
