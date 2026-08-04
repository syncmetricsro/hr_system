"""Build the smallest deterministic workbook that exercises the HV importer.

The client's filled workbook is intentionally gitignored.  Tests must still
cover the structural surprises observed in it, so this module creates an OOXML
archive with the same relevant rows, formulas, totals and unnamed columns using
only the standard library.
"""

from __future__ import annotations

import zipfile
from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

PROJECT_COLUMNS = ("B", "C", "D", "E", "F", "J", "K", "L", "M")
COST_ROWS = {
    4: "hrubá výplata bez zrážok",
    5: "szco",
    6: "odvody",
    7: "vodič",
    8: "škoda",
    9: "vzv oktatas",
    10: "vzv jogsi",
    11: "ubytovanie",
    12: "poistenie",
    13: "lekarske",
    14: "koordinatorok",
    15: "leasingek",
    16: "benzin",
    17: "myto",
    18: "faktoring",
    19: "iroda",
    20: "toborzas",
    21: "hr",
    22: "oblecenie",
    23: "iné náklady mimoriadne",
}
REVENUE_ROWS = {
    25: "škoda",
    26: "faktúry",
    27: "zrážky prijaté od zam",
    30: "obed",
    31: "ubytovňa",
}


def build_hv_test_workbook(path: Path) -> Path:
    """Write a private-data-free workbook analogue and return its path."""
    cells: dict[tuple[str, int], tuple[str, str, str | None]] = {}

    def text(column: str, row: int, value: str) -> None:
        cells[(column, row)] = ("text", value, None)

    def number(
        column: str, row: int, value: str | Decimal, formula: str | None = None
    ) -> None:
        cells[(column, row)] = ("number", str(value), formula)

    text("A", 3, "NAKLADY")
    number("B", 3, "95")  # The real sheet puts headcount inside its cost range.

    for row, label in COST_ROWS.items():
        # The filled source has no left-hand label for gross wage.  The second
        # label column is therefore part of the importer's contract.
        text("I" if row == 4 else "A", row, label)
    text("A", 24, "celkové náklady")
    for row, label in REVENUE_ROWS.items():
        text("A", row, label)
    text("A", 32, "celkové výnosy")

    for column in PROJECT_COLUMNS:
        for row in COST_ROWS:
            number(column, row, "-10")
        for row in REVENUE_ROWS:
            number(column, row, "10")

    # Column B carries binary-float noise, a stray headcount in B3 and a stale
    # cached total.  Its category cells themselves sum to -19096.90.
    number("B", 4, "-18676.900000000001")
    number("B", 5, "-60")
    for row in range(6, 24):
        number("B", row, "-20")

    # Column C has the specific values used in the accounting assertions.  Its
    # own category cells total -15187.17 while the cached total says -15087.17.
    for row in COST_ROWS:
        number("C", row, "-100")
    number("C", 4, "-7351.03")
    number("C", 5, "-770")
    number("C", 6, "-5266.14")
    number("C", 23, "-200")
    number("C", 26, "14246.26")

    # The same label appears once in each sign block.
    number("F", 8, "-8000")
    number("F", 25, "4550")

    # G is populated among category rows but is not a project column.  The
    # operator must acknowledge it with --ignore instead of the importer
    # guessing what it represents.
    number("G", 30, "23")
    number("G", 31, "42")

    cost_totals = {
        "B": "-18996.90",
        "C": "-15087.17",
        "D": "-200",
        "E": "-200",
        "F": "-8190",
        "J": "-200",
        "K": "-200",
        "L": "-200",
        "M": "-200",
    }
    revenue_totals = {
        "B": "50",
        "C": "14286.26",
        "D": "50",
        "E": "50",
        "F": "4590",
        "J": "50",
        "K": "50",
        "L": "50",
        "M": "50",
    }
    for column in PROJECT_COLUMNS:
        cost_formula = f"SUM({column}3:{column}{22 if column == 'C' else 23})"
        number(column, 24, cost_totals[column], cost_formula)
        number(column, 32, revenue_totals[column], f"SUM({column}25:{column}31)")

    rows: dict[int, list[str]] = {}
    for (column, row), (kind, value, formula) in cells.items():
        reference = f"{column}{row}"
        if kind == "text":
            xml = (
                f'<c r="{reference}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
            )
        else:
            formula_xml = f"<f>{escape(formula)}</f>" if formula else ""
            xml = f'<c r="{reference}">{formula_xml}<v>{escape(value)}</v></c>'
        rows.setdefault(row, []).append(xml)

    sheet_rows = "".join(
        f'<row r="{row}">{"".join(entries)}</row>'
        for row, entries in sorted(rows.items())
    )
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main"><sheetData>'
        f"{sheet_rows}</sheetData></worksheet>"
    )

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    return path
