import csv
import io
from collections.abc import Iterator
from datetime import datetime

import xlsxwriter

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

TEAM_HEADERS = ["Team", "Members", "Captain", "Captain email", "Registered at (UTC)"]

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

_DATETIME_FORMAT = "%Y-%m-%d %H:%M"
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
# Text is written as text, never as a formula, link or number, so participant input cannot
# run in Excel and NU IDs keep any leading zeros.
_WORKBOOK_OPTIONS = {
    "in_memory": True,
    "strings_to_formulas": False,
    "strings_to_urls": False,
    "strings_to_numbers": False,
    "remove_timezone": True,
    "default_date_format": "yyyy-mm-dd hh:mm",
}
_MAX_COLUMN_WIDTH = 50

Cell = str | int | datetime


def _member_rows(team: Team) -> Iterator[list[Cell]]:
    for number, member in enumerate(team.members, start=1):
        yield [
            team.name,
            team.created_at,
            number,
            "yes" if member.is_captain else "",
            member.full_name,
            member.email,
            member.nu_id or "",
            YEAR_LABELS.get(member.year_of_study, member.year_of_study),
            member.major,
        ]


def _team_row(team: Team) -> list[Cell]:
    captain = next((m for m in team.members if m.is_captain), None)
    return [
        team.name,
        len(team.members),
        captain.full_name if captain else "",
        captain.email if captain else "",
        team.created_at,
    ]


def _display(value: Cell) -> str:
    return value.strftime(_DATETIME_FORMAT) if isinstance(value, datetime) else str(value)


def _csv_cell(value: Cell) -> str:
    """Stop spreadsheet apps from executing participant-supplied text as a formula."""
    text = _display(value)
    return f"'{text}" if text.startswith(_FORMULA_PREFIXES) else text


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
        for row in _member_rows(team):
            writer.writerow([_csv_cell(cell) for cell in row])
        yield flush()


def _column_width(header: str, values: list[Cell]) -> int:
    longest = max([len(header), *(len(_display(v)) for v in values)])
    return min(longest + 2, _MAX_COLUMN_WIDTH)


def _write_sheet(sheet, header_format, headers: list[str], rows: list[list[Cell]]) -> None:
    sheet.write_row(0, 0, headers, header_format)
    for index, row in enumerate(rows, start=1):
        sheet.write_row(index, 0, row)
    for column, header in enumerate(headers):
        sheet.set_column(column, column, _column_width(header, [row[column] for row in rows]))
    sheet.freeze_panes(1, 0)
    sheet.autofilter(0, 0, len(rows), len(headers) - 1)


def teams_xlsx(teams: list[Team]) -> bytes:
    """A Participants sheet (one row per member, as in the CSV) and a Teams summary sheet."""
    buffer = io.BytesIO()
    with xlsxwriter.Workbook(buffer, _WORKBOOK_OPTIONS) as workbook:
        header_format = workbook.add_format(
            {"bold": True, "font_color": "#FFFFFF", "bg_color": "#00629C"}
        )
        participants = [row for team in teams for row in _member_rows(team)]
        _write_sheet(workbook.add_worksheet("Participants"), header_format, HEADERS, participants)
        team_rows = [_team_row(team) for team in teams]
        _write_sheet(workbook.add_worksheet("Teams"), header_format, TEAM_HEADERS, team_rows)
    return buffer.getvalue()
