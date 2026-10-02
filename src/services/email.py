import asyncio
import logging
import smtplib
from email.message import EmailMessage

from core.config import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(settings.smtp_host and settings.mail_from)


def _deliver(message: EmailMessage) -> None:
    host, port = settings.smtp_host, settings.smtp_port
    if port == 465:
        server = smtplib.SMTP_SSL(host, port, timeout=20)
    else:
        server = smtplib.SMTP(host, port, timeout=20)
        server.starttls()
    with server:
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)


async def send(to: list[str], subject: str, text: str, html: str | None = None) -> bool:
    """Send one email. Never raises: a mail outage must not break the caller."""
    if not is_configured() or not to:
        return False
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = ", ".join(to)
    message["Subject"] = subject
    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")
    try:
        await asyncio.to_thread(_deliver, message)
    except Exception:
        logger.exception("failed to send email %r to %d recipients", subject, len(to))
        return False
    logger.info("sent email %r to %d recipients", subject, len(to))
    return True
