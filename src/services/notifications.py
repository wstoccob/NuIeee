from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from core.clock import as_utc
from core.config import settings
from models.big_event import BigEvent
from models.team import Team


def team_link(token: str) -> str:
    # The secret goes in the fragment, which browsers never send to any server.
    return f"{settings.public_site_url.rstrip('/')}/hackathon/team#{token}"


def _when(value: datetime | None) -> str | None:
    if value is None:
        return None
    zone = ZoneInfo(settings.mail_time_zone)
    return (
        as_utc(value).astimezone(zone).strftime("%a %d %b, %H:%M") + f" ({settings.mail_time_zone})"
    )


def _schedule(event: BigEvent) -> list[str]:
    lines = []
    if opens := _when(event.case_selection_opens_at):
        lines.append(f"Case selection opens: {opens}")
    if closes := _when(event.submissions_close_at):
        lines.append(f"Submission deadline: {closes}")
    return lines


def _compose(team: Team, event: BigEvent, link: str, rotated: bool) -> tuple[str, str, str]:
    subject = f"Your team link for {event.title}"
    intro = (
        f"The organisers issued a new link for {team.name}. The previous link no longer works."
        if rotated
        else f"{team.name} is registered for {event.title}."
    )
    schedule = _schedule(event)

    text = "\n".join(
        [
            intro,
            "",
            "Your team page, where you choose a case and upload your solution:",
            link,
            "",
            "Keep this link private and share it only with your teammates: anyone who has it",
            "can change your case and submission. It is the only way into your team page.",
            "",
            *schedule,
            "",
            "NU IEEE Student Branch",
        ]
    )
    schedule_html = "".join(f"<li>{escape(line)}</li>" for line in schedule)
    html = f"""\
<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;
            color:#1f2933;max-width:560px">
  <p>{escape(intro)}</p>
  <p>Your team page, where you choose a case and upload your solution:</p>
  <p><a href="{escape(link, quote=True)}"
        style="display:inline-block;background:#00629C;color:#ffffff;padding:12px 20px;
               border-radius:8px;text-decoration:none;font-weight:bold">Open team page</a></p>
  <p style="font-size:13px;color:#52606d;word-break:break-all">{escape(link)}</p>
  <p><strong>Keep this link private</strong> and share it only with your teammates: anyone who
     has it can change your case and submission. It is the only way into your team page.</p>
  {f"<ul>{schedule_html}</ul>" if schedule_html else ""}
  <p style="color:#52606d">NU IEEE Student Branch</p>
</div>"""
    return subject, text, html


def team_link_email(
    team: Team, event: BigEvent, token: str, *, rotated: bool = False
) -> tuple[list[str], str, str, str]:
    """Build the email while the request still has its database session.

    Sending happens in a background task after the response, when ORM objects are
    detached, so only plain strings cross that boundary.
    """
    subject, text, html = _compose(team, event, team_link(token), rotated)
    return [member.email for member in team.members], subject, text, html
