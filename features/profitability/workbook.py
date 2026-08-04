"""Read Jober's HV workbook with the standard library only.

An `.xlsx` is a zip of XML, so `zipfile` plus a little parsing is enough to get
every cell. That keeps a spreadsheet parser out of the dependency set entirely —
AGENTS.md §3.1 would otherwise require an ADR, a release cooldown and a
hash-pinned lock update for a file we read a handful of times a year.

Deliberately minimal: this reads values and formulas from the first worksheet
and nothing else. No styles, no dates, no merged-cell resolution. If the source
ever needs more than that, it is a reason to revisit the dependency decision
rather than to grow this file into a spreadsheet library.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html import unescape

_CELL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*)>(.*?)</c>', re.S)
_VALUE = re.compile(r"<v>(.*?)</v>", re.S)
_INLINE = re.compile(r"<is>.*?<t[^>]*>(.*?)</t>", re.S)
_FORMULA = re.compile(r"<f[^>]*>(.*?)</f>", re.S)
_TYPE = re.compile(r't="([^"]+)"')
_SHARED = re.compile(r"<si>(.*?)</si>", re.S)
_TEXT = re.compile(r"<t[^>]*>(.*?)</t>", re.S)


class WorkbookError(Exception):
    """The file is not a readable workbook, or lacks the sheet we need."""


@dataclass(frozen=True)
class Cell:
    text: str
    number: Decimal | None
    formula: str | None


def column_index(column: str) -> int:
    """``A`` -> 1, ``Z`` -> 26, ``AA`` -> 27. Used only for ordering columns."""
    index = 0
    for character in column:
        index = index * 26 + (ord(character) - 64)
    return index


def read_sheet(path) -> dict[tuple[str, int], Cell]:
    """Every populated cell of the first worksheet, keyed ``(column, row)``."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            sheet_name = next(
                (n for n in sorted(names) if n.startswith("xl/worksheets/sheet")),
                None,
            )
            if sheet_name is None:
                raise WorkbookError("The workbook contains no worksheet.")
            sheet = archive.read(sheet_name).decode("utf-8")
            shared = []
            if "xl/sharedStrings.xml" in names:
                blob = archive.read("xl/sharedStrings.xml").decode("utf-8")
                shared = [
                    unescape("".join(_TEXT.findall(item)))
                    for item in _SHARED.findall(blob)
                ]
    except zipfile.BadZipFile as exc:  # not an xlsx at all
        raise WorkbookError(f"{path} is not a readable .xlsx file.") from exc

    cells: dict[tuple[str, int], Cell] = {}
    for match in _CELL.finditer(sheet):
        column, row, attrs, body = (
            match.group(1),
            int(match.group(2)),
            match.group(3),
            match.group(4),
        )
        kind = _TYPE.search(attrs)
        raw = _VALUE.search(body)
        inline = _INLINE.search(body)
        formula = _FORMULA.search(body)

        text, number = "", None
        if inline:
            text = unescape(inline.group(1))
        elif raw is not None:
            value = raw.group(1)
            if kind and kind.group(1) == "s":
                try:
                    text = shared[int(value)]
                except (IndexError, ValueError):
                    text = ""
            elif kind and kind.group(1) == "str":
                text = unescape(value)
            else:
                try:
                    number = Decimal(value)
                except (InvalidOperation, ValueError):
                    text = unescape(value)
        if text or number is not None or formula:
            cells[(column, row)] = Cell(
                text=text.strip(),
                number=number,
                formula=unescape(formula.group(1)) if formula else None,
            )
    return cells


def quantize(amount: Decimal) -> Decimal:
    """Two decimal places. The source carries binary-float noise — one cell
    reads ``-18676.900000000001`` — and money must not."""
    return amount.quantize(Decimal("0.01"))
