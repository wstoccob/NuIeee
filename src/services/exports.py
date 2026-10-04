import csv
import io
from collections.abc import Iterator

from models.team import Team, YearOfStudy

YEAR_LABELS = {
    YearOfStudy.FIRST: "1st",
    YearOfStudy.SECOND: "2nd",
    YearOfStudy.THIRD: "3rd",
    YearOfStudy.FOURTH: "4th",
    YearOfStudy.NOT_APPLICABLE: "Not applicable",
}

HEADERS = [
    "Team",
    "Registered at (UTC)",
    "Member #",
    "Captain",
    "Full name",
    "Email",
    "NU ID",
    "Year of study",
    "Major",
]

_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _safe(value: object) -> str:
    """Stop spreadsheet apps from executing participant-supplied text as a formula."""
    text = "" if value is None else str(value)
    return f"'{text}" if text.startswith(_FORMULA_PREFIXES) else text


def _rows(team: Team) -> Iterator[list[str]]:
    team_cells = [team.name, team.created_at.strftime("%Y-%m-%d %H:%M")]
    for number, member in enumerate(team.members, start=1):
        yield [
            *team_cells,
            str(number),
            "yes" if member.is_captain else "",
            member.full_name,
            member.email,
            member.nu_id or "",
            YEAR_LABELS.get(member.year_of_study, member.year_of_study),
            member.major,
        ]


def teams_csv(teams: list[Team]) -> Iterator[str]:
    """One row per member, UTF-8 with BOM so Excel shows Cyrillic names correctly."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    def flush() -> str:
        chunk = buffer.getvalue()
        buffer.seek(0)
        buffer.truncate()
        return chunk

    writer.writerow(HEADERS)
    yield "﻿" + flush()
    for team in teams:
        for row in _rows(team):
            writer.writerow([_safe(cell) for cell in row])
        yield flush()
