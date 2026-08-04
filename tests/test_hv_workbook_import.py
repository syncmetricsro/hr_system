"""Importing Jober's real HV workbook.

These run against `docs/examples/HV 202510.xlsx` itself rather than a fixture,
because the things worth testing are the ways that specific file misbehaves:

* two of its nine projects have **no name anywhere in the sheet** (columns B and
  J carry a headcount in the header row), so the importer must refuse to guess;
* a column that is not a project holds figures inside category rows (`G30`,
  `G31`), so "has numbers" cannot mean "is a project";
* its cached totals disagree with its own cells in two columns, and `B3` puts a
  headcount inside the summed cost block.

A fixture reproducing all that would just be the file with extra steps.
"""

from __future__ import annotations

from decimal import Decimal
from io import StringIO
from pathlib import Path

import pytest
from django.apps import apps as django_apps
from django.core.management import CommandError, call_command

if not django_apps.is_installed("features.profitability"):
    pytest.skip(
        "features.profitability is not installed for this client",
        allow_module_level=True,
    )

from core.offices.models import Office  # noqa: E402
from core.projects.models import Project  # noqa: E402
from features.profitability.models import (  # noqa: E402
    FinanceCategory,
    FinanceCategoryKind,
    FinanceLineItem,
    FinancialMonth,
)
from features.profitability.workbook import WorkbookError, read_sheet  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

WORKBOOK = Path("docs/examples/HV 202510.xlsx")
PERIOD = "2025-11"

# Column -> (project code, office). Columns B and J are named from
# Jober_Finance_Specs §3, not from the file — that is the whole point.
COLUMNS = [
    ("B", "RLS", "VM"),
    ("C", "MINIT", "VM"),
    ("D", "MEVIS", "VM"),
    ("E", "DHLG", "VM"),
    ("F", "DHLBA", "VM"),
    ("J", "PIVO", "DS"),
    ("K", "MEDIA", "DS"),
    ("L", "EURO", "DS"),
    ("M", "DELT", "DS"),
]


@pytest.fixture
def catalogue():
    call_command("seed_finance", stdout=StringIO())
    return {c.key: c for c in FinanceCategory.objects.exclude(key="")}


@pytest.fixture
def projects():
    offices = {
        "VM": Office.objects.create(name="Megyer", code="VM", country="SK"),
        "DS": Office.objects.create(name="Dunajská Streda", code="DS", country="SK"),
    }
    made = {}
    for _column, code, office in COLUMNS:
        made[code] = Project.objects.create(
            name=code,
            code=code,
            office=offices[office],
            is_active=True,
            financial_reporting_eligible=True,
        )
    return made


def _import(*extra, **kwargs):
    out = StringIO()
    args = [str(WORKBOOK), "--period", PERIOD]
    for column, code, _office in COLUMNS:
        args += ["--map", f"{column}={code}"]
    args += ["--ignore", "G", *extra]
    call_command("import_hv_workbook", *args, stdout=out, **kwargs)
    return out.getvalue()


# --- refusing to guess -----------------------------------------------------


def test_it_refuses_when_a_populated_column_has_no_mapping(catalogue, projects):
    """Columns B and J are unnamed in the sheet. Importing them by position
    would file a month against the wrong project and look entirely normal."""
    with pytest.raises(CommandError) as excinfo:
        call_command(
            "import_hv_workbook",
            str(WORKBOOK),
            "--period",
            PERIOD,
            "--map",
            "C=MINIT",
            "--ignore",
            "G",
            stdout=StringIO(),
        )

    message = str(excinfo.value)
    assert "B" in message and "J" in message
    assert FinanceLineItem.objects.count() == 0


def test_a_non_project_column_must_be_ignored_explicitly(catalogue, projects):
    """`G` holds headcounts inside two category rows, so it reads as populated.
    Excluding it is a decision the operator states."""
    args = [str(WORKBOOK), "--period", PERIOD]
    for column, code, _office in COLUMNS:
        args += ["--map", f"{column}={code}"]

    with pytest.raises(CommandError) as excinfo:
        call_command("import_hv_workbook", *args, stdout=StringIO())

    assert "G" in str(excinfo.value)


def test_a_column_cannot_be_both_mapped_and_ignored(catalogue, projects):
    with pytest.raises(CommandError, match="both mapped and ignored"):
        _import("--ignore", "C")


def test_an_unknown_project_code_is_refused(catalogue, projects):
    """Every column mapped, so this gets past the mapping check and fails on
    the code itself — otherwise the earlier guard masks what is being tested."""
    args = [str(WORKBOOK), "--period", PERIOD]
    for column, code, _office in COLUMNS:
        args += ["--map", f"{column}={'NOPE' if column == 'C' else code}"]
    args += ["--ignore", "G"]

    with pytest.raises(CommandError, match="No project with code"):
        call_command("import_hv_workbook", *args, stdout=StringIO())

    assert FinanceLineItem.objects.count() == 0


# --- reading the cells -----------------------------------------------------


def test_it_imports_every_project_and_category(catalogue, projects):
    _import()

    assert FinancialMonth.objects.count() == len(COLUMNS)
    minit = FinancialMonth.objects.get(project__code="MINIT", year=2025, month=11)
    by_key = {
        i.category.key: i.amount for i in minit.line_items.select_related("category")
    }

    # Storage keeps magnitudes; the workbook's negatives are the input convention.
    assert by_key["gross_wage"] == Decimal("7351.03")
    assert by_key["levies"] == Decimal("5266.14")
    assert by_key["other_extraordinary"] == Decimal("200.00")
    assert by_key["invoices"] == Decimal("14246.26")


def test_damage_is_split_into_cost_and_recovered_revenue(catalogue, projects):
    """`škoda` is a row in both blocks. Only the row number distinguishes them,
    so a label-only mapping would collapse two categories into one."""
    _import()

    dhlba = FinancialMonth.objects.get(project__code="DHLBA", year=2025, month=11)
    by_key = {i.category.key: i for i in dhlba.line_items.select_related("category")}

    assert by_key["damage_cost"].category.kind == FinanceCategoryKind.COST
    assert by_key["damage_cost"].amount == Decimal("8000.00")
    assert by_key["damage_recovered"].category.kind == FinanceCategoryKind.REVENUE
    assert by_key["damage_recovered"].amount == Decimal("4550.00")


def test_binary_float_noise_is_quantised(catalogue, projects):
    """`B4` reads -18676.900000000001 in the file. Money does not."""
    _import()

    rls = FinancialMonth.objects.get(project__code="RLS", year=2025, month=11)
    wage = rls.line_items.get(category__key="gross_wage")
    assert wage.amount == Decimal("18676.90")


def test_totals_rows_are_never_imported_as_categories(catalogue, projects):
    """`celkové náklady` and `celkové výnosy` are the workbook's own sums."""
    _import()

    labels = set(
        FinanceLineItem.objects.values_list("category__label", flat=True).distinct()
    )
    assert not {"celkové náklady", "celkové výnosy"} & labels


# --- reporting the workbook's own errors -----------------------------------


def test_it_reports_where_the_workbook_disagrees_with_itself(catalogue, projects):
    """The point of recomputing. Column C is the defect Jober_Finance_Specs §7
    records; column B is a second one the spec does not mention. Both are
    reported rather than silently corrected."""
    output = _import()

    assert "column C: workbook costs total -15087.17" in output
    assert "its own cells sum to -15187.17" in output
    assert "column B: workbook costs total -18996.90" in output
    assert "Imported the cells." in output


def test_the_stray_headcount_inside_the_cost_block_is_not_imported(catalogue, projects):
    """`B3` holds a headcount in the row the workbook's own SUM range starts at.
    Summing categories rather than a coordinate range excludes it."""
    _import()

    rls = FinancialMonth.objects.get(project__code="RLS", year=2025, month=11)
    total = sum(
        (
            i.amount
            for i in rls.line_items.select_related("category")
            if i.category.kind == FinanceCategoryKind.COST
        ),
        Decimal("0"),
    )
    assert total == Decimal("19096.90")


# --- operational behaviour -------------------------------------------------


def test_dry_run_writes_nothing(catalogue, projects):
    output = _import("--dry-run")

    assert "Would import" in output
    assert FinanceLineItem.objects.count() == 0
    assert FinancialMonth.objects.count() == 0


def test_import_is_idempotent(catalogue, projects):
    _import()
    first = FinanceLineItem.objects.count()

    _import()

    assert FinanceLineItem.objects.count() == first


def test_a_locked_month_is_refused(catalogue, projects):
    _import()
    month = FinancialMonth.objects.get(project__code="MINIT")
    month.is_locked = True
    month.save(update_fields=["is_locked"])

    with pytest.raises(CommandError, match="locked"):
        _import()


def test_a_bad_period_is_rejected(catalogue, projects):
    with pytest.raises(CommandError, match="YYYY-MM"):
        call_command(
            "import_hv_workbook",
            str(WORKBOOK),
            "--period",
            "November",
            "--map",
            "C=MINIT",
            "--ignore",
            "G",
            stdout=StringIO(),
        )


def test_a_non_workbook_file_fails_cleanly(tmp_path, catalogue, projects):
    junk = tmp_path / "not-a-workbook.xlsx"
    junk.write_text("this is not a zip")

    with pytest.raises(CommandError, match="not a readable"):
        call_command(
            "import_hv_workbook",
            str(junk),
            "--period",
            PERIOD,
            "--map",
            "C=MINIT",
            stdout=StringIO(),
        )


# --- the reader itself -----------------------------------------------------


def test_the_reader_returns_values_and_formulas():
    cells = read_sheet(WORKBOOK)

    assert cells[("A", 3)].text == "NAKLADY"
    assert cells[("C", 4)].number == Decimal("-7351.03")
    # The defect, straight from the file.
    assert cells[("C", 24)].formula == "SUM(C3:C22)"
    assert cells[("D", 24)].formula == "SUM(D3:D23)"


def test_the_reader_rejects_a_non_zip():
    with pytest.raises(WorkbookError):
        read_sheet(__file__)


# --- the bookkeeper export -------------------------------------------------


def test_the_csv_carries_the_spec_columns(
    client, django_user_model, catalogue, projects
):
    """Jober_Finance_Specs §8 names the columns. `category_key` and
    `project_name` matter most: a bookkeeper reads names, anything downstream
    joins on keys, and keys survive a label being retranslated.
    """
    import csv
    from django.urls import reverse

    _import()
    manager = django_user_model.objects.create_user(
        email="csv-mgr@demo.jober.test", password="x", role="manager"
    )
    # Give the manager both offices. Without a membership `user_office_scope`
    # returns an empty queryset, the export is correctly empty, and this test
    # would assert nothing while looking like it passed.
    manager.offices.set(Office.objects.all())
    client.force_login(manager)

    response = client.get(reverse("export_finance"))
    assert response.status_code == 200
    rows = list(csv.reader(response.content.decode("utf-8").splitlines()))

    header = rows[0]
    for column in (
        "period",
        "office",
        "project_code",
        "project_name",
        "category_key",
        "category_label",
        "kind",
        "group",
        "amount_eur",
    ):
        assert column in header, f"{column} missing from the export header"

    # Every row, including the summary rows, must be the same width or the file
    # is not machine-readable regardless of what the header promises.
    assert {len(r) for r in rows if r} == {len(header)}

    line_rows = [r for r in rows if r and r[0] == "line"]
    key_index = header.index("category_key")
    assert all(r[key_index] for r in line_rows), "a line row has no category key"

    # Costs export signed, matching the source workbook.
    amount_index = header.index("amount_eur")
    kind_index = header.index("kind")
    costs = [r for r in line_rows if r[kind_index] == "cost"]
    assert costs and all(Decimal(r[amount_index]) <= 0 for r in costs)
