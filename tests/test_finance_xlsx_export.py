from __future__ import annotations

import re
from decimal import Decimal
from io import BytesIO
from zipfile import ZipFile

import pytest
from django.apps import apps as django_apps
from django.urls import reverse
from django.utils import translation
from xml.etree import ElementTree

if not django_apps.is_installed("features.profitability"):
    pytest.skip(
        "features.profitability is not installed for this client",
        allow_module_level=True,
    )

from core.accounts.models import Role  # noqa: E402
from core.offices.models import Office  # noqa: E402
from core.projects.models import Project  # noqa: E402
from features.profitability.models import (  # noqa: E402
    FinanceCategory,
    FinanceCategoryKind,
    FinancialMonth,
)
from features.profitability.services import recompute_month, set_line_item  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _project(name, code, office):
    return Project.objects.create(
        name=name,
        code=code,
        office=office,
        is_active=True,
        financial_reporting_eligible=True,
    )


def _manager(django_user_model, office):
    user = django_user_model.objects.create_user(
        email="xlsx-manager@demo.jober.test",
        password="x",
        role=Role.MANAGER,
    )
    user.offices.add(office)
    return user


def _column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference).group(0)
    value = 0
    for letter in letters:
        value = value * 26 + ord(letter) - ord("A") + 1
    return value - 1


def _worksheet_rows(archive: ZipFile, path: str) -> list[list[str | Decimal | None]]:
    shared_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    shared = [
        "".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t"))
        for item in shared_root.findall(f"{{{MAIN_NS}}}si")
    ]
    sheet_root = ElementTree.fromstring(archive.read(path))
    rows = []
    for row in sheet_root.findall(f".//{{{MAIN_NS}}}row"):
        values: list[str | Decimal | None] = []
        for cell in row.findall(f"{{{MAIN_NS}}}c"):
            column = _column_index(cell.attrib["r"])
            while len(values) <= column:
                values.append(None)
            value = cell.find(f"{{{MAIN_NS}}}v")
            if value is None:
                continue
            values[column] = (
                shared[int(value.text)]
                if cell.attrib.get("t") == "s"
                else Decimal(value.text)
            )
        rows.append(values)
    return rows


def test_finance_xlsx_is_scoped_formula_free_and_contains_live_charts(
    client, django_user_model
):
    own_office = Office.objects.create(name="Own Office", code="OWN", country="SK")
    hidden_office = Office.objects.create(
        name="Hidden Office", code="HID", country="SK"
    )
    own_project = _project("https://plain-text.example", "OWN-P", own_office)
    hidden_project = _project("Hidden Project", "HIDDEN-P", hidden_office)
    cost = FinanceCategory.objects.create(
        key="wage", label="=NotAFormula", kind=FinanceCategoryKind.COST, order=1
    )
    revenue = FinanceCategory.objects.create(
        key="invoice",
        label="Client invoices",
        kind=FinanceCategoryKind.REVENUE,
        order=1,
    )

    own_month = FinancialMonth.objects.create(project=own_project, year=2026, month=1)
    set_line_item(own_month, cost, Decimal("100"))
    set_line_item(own_month, revenue, Decimal("300"))
    recompute_month(own_month)
    hidden_month = FinancialMonth.objects.create(
        project=hidden_project, year=2026, month=1
    )
    set_line_item(hidden_month, cost, Decimal("999"))
    set_line_item(hidden_month, revenue, Decimal("1999"))
    recompute_month(hidden_month)

    client.force_login(_manager(django_user_model, own_office))
    with translation.override("en"):
        export_url = reverse("export_finance_xlsx", args=[2026])
    response = client.get(export_url, HTTP_ACCEPT_LANGUAGE="en")

    assert response.status_code == 200
    assert response["Content-Type"] == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response["Content-Disposition"] == (
        'attachment; filename="finance-2026.xlsx"'
    )

    with ZipFile(BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        sheet_names = [
            sheet.attrib["name"] for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet")
        ]
        assert sheet_names == ["Year", "Months"]
        assert {"xl/charts/chart1.xml", "xl/charts/chart2.xml"} <= names
        assert not any(name.startswith("xl/externalLinks/") for name in names)
        assert not any("vbaProject" in name for name in names)

        for sheet_path in ("xl/worksheets/sheet1.xml", "xl/worksheets/sheet2.xml"):
            root = ElementTree.fromstring(archive.read(sheet_path))
            assert root.find(f".//{{{MAIN_NS}}}f") is None

        shared_strings = archive.read("xl/sharedStrings.xml").decode("utf-8")
        assert "=NotAFormula" in shared_strings
        assert "https://plain-text.example" in shared_strings
        assert "Hidden Project" not in shared_strings
        assert "Hidden Office" not in shared_strings

        year_rows = _worksheet_rows(archive, "xl/worksheets/sheet1.xml")
        cost_row = next(row for row in year_rows if row[0] == "=NotAFormula")
        revenue_row = next(row for row in year_rows if row[0] == "Client invoices")
        result_row = next(row for row in year_rows if row[0] == "Profit/loss")
        assert cost_row[1] == Decimal("-100")
        assert revenue_row[1] == Decimal("300")
        assert result_row[1] == Decimal("200")

        month_rows = _worksheet_rows(archive, "xl/worksheets/sheet2.xml")
        january = next(row for row in month_rows if row[0] == "2026-01")
        february = next(row for row in month_rows if row[0] == "2026-02")
        assert january[1:4] == [Decimal("300"), Decimal("-100"), Decimal("200")]
        assert february[1:4] == [Decimal("0"), Decimal("0"), Decimal("0")]


def test_finance_xlsx_requires_approved_export_permission(client, django_user_model):
    recruiter = django_user_model.objects.create_user(
        email="xlsx-recruiter@demo.jober.test",
        password="x",
        role=Role.RECRUITER,
    )
    client.force_login(recruiter)

    assert client.get(reverse("export_finance_xlsx", args=[2026])).status_code == 403


def test_finance_pages_link_to_the_selected_year_export(client, django_user_model):
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    client.force_login(_manager(django_user_model, office))
    expected = reverse("export_finance_xlsx", args=[2026])

    assert expected in client.get(reverse("finance_year", args=[2026])).content.decode()
