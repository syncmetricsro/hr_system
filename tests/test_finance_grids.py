"""The workbook grid and the year grid.

Jober will accept the implementation when it totals like their own
`HV 202510.xlsx`, so these assert the properties that workbook gets wrong.

* **Costs are signed at the boundary.** Storage keeps magnitudes with `kind`
  carrying the sign; the grid renders costs negative, as the source does.
* **Totals are recomputed from the category set, never from a coordinate
  range.** `Jober_Finance_Specs` §7 records that `C24=SUM(C3:C22)` stops one row
  short and drops Minit's -200.

  Checking the file directly found that is not the whole story: **the cached
  totals in columns B and C match neither `SUM(:22)` nor `SUM(:23)`** — Minit's
  is 100 away from both — so those cells are stale as well as wrongly ranged.
  Column B also carries a headcount (`B3=3`) *inside* the summed cost block.
  Three separate ways for a spreadsheet total to be wrong, which is why nothing
  here reproduces a cached figure: the tests assert the computation instead.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.apps import apps as django_apps

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
    FinancialMonth,
)
from features.profitability.services import (  # noqa: E402
    project_year_grid,
    set_line_item,
    workbook_grid,
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

YEAR, MONTH = 2025, 11


@pytest.fixture
def catalog():
    """The three categories these tests move money through."""
    return {
        "wage": FinanceCategory.objects.create(
            label="Gross wage", kind=FinanceCategoryKind.COST, order=1
        ),
        "extra": FinanceCategory.objects.create(
            label="Other extraordinary costs", kind=FinanceCategoryKind.COST, order=20
        ),
        "invoices": FinanceCategory.objects.create(
            label="Client invoices", kind=FinanceCategoryKind.REVENUE, order=1
        ),
    }


def _project(name, office, code=None):
    return Project.objects.create(
        name=name,
        code=code or name[:8].upper(),
        office=office,
        is_active=True,
        financial_reporting_eligible=True,
    )


def _month(project):
    return FinancialMonth.objects.create(project=project, year=YEAR, month=MONTH)


def _fill(month, catalog, *, wage=None, extra=None, invoices=None):
    if wage is not None:
        set_line_item(month, catalog["wage"], Decimal(wage))
    if extra is not None:
        set_line_item(month, catalog["extra"], Decimal(extra))
    if invoices is not None:
        set_line_item(month, catalog["invoices"], Decimal(invoices))


# --- the workbook grid -----------------------------------------------------


def test_every_category_is_summed_including_the_last(catalog):
    """The defect class the source workbook demonstrates.

    `C24=SUM(C3:C22)` stops one row short of the cost block, so Minit's -200
    extraordinary cost never reaches its total. Here the grid must include the
    last category in the ordering — the whole reason totals are computed from
    the category set rather than a coordinate range.
    """
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    month = _month(_project("Minit", office))
    # `extra` is the highest `order`, i.e. the row a short range would drop.
    _fill(month, catalog, wage="7351.03", extra="200", invoices="15366.26")

    column = workbook_grid(YEAR, MONTH)["columns"][0]

    assert column["cost"] == Decimal("-7551.03")
    assert column["revenue"] == Decimal("15366.26")
    assert column["net"] == Decimal("7815.23")
    # Drop the last category and the total must move by exactly its amount —
    # which is what the workbook silently does.
    month.line_items.filter(category=catalog["extra"]).delete()
    assert workbook_grid(YEAR, MONTH)["columns"][0]["net"] == Decimal("8015.23")


def test_costs_render_negative_and_revenues_positive(catalog):
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    _fill(_month(_project("Minit", office)), catalog, wage="100", invoices="250")

    grid = workbook_grid(YEAR, MONTH)
    cost_values = grid["cost_rows"][0]["values"]
    revenue_values = grid["revenue_rows"][0]["values"]

    assert cost_values[0] == Decimal("-100")
    assert revenue_values[0] == Decimal("250")


def test_rows_align_with_columns_even_when_a_cell_is_empty(catalog):
    """A row's values are positional, so a project with no entry for a category
    must leave a `None` hole rather than shifting every later column left."""
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    _fill(_month(_project("Alpha", office, code="ALPHA")), catalog, wage="100")
    _fill(_month(_project("Beta", office, code="BETA")), catalog, invoices="50")

    grid = workbook_grid(YEAR, MONTH)

    assert len(grid["columns"]) == 2
    for row in grid["cost_rows"] + grid["revenue_rows"]:
        assert len(row["values"]) == 2
    wage_row = next(r for r in grid["cost_rows"] if r["category"].label == "Gross wage")
    assert wage_row["values"] == [Decimal("-100"), None]


def test_office_subtotals_and_grand_total(catalog):
    """`Summ DS` and `Summ Spolu` in the source."""
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    ds = Office.objects.create(name="Dunajská Streda", code="DS", country="SK")
    _fill(_month(_project("Minit", vm)), catalog, wage="100", invoices="300")
    _fill(_month(_project("Europack", ds)), catalog, wage="50", invoices="200")

    grid = workbook_grid(YEAR, MONTH)
    by_office = {o["office"]: o for o in grid["offices"]}

    assert by_office["Velký Meder"]["net"] == Decimal("200")
    assert by_office["Dunajská Streda"]["net"] == Decimal("150")
    assert grid["grand"]["net"] == Decimal("350")
    assert grid["grand"]["cost"] == Decimal("-150")


def test_the_grid_is_office_scoped(catalog):
    """The workbook has no concept of an office boundary and the product does."""
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    ds = Office.objects.create(name="Dunajská Streda", code="DS", country="SK")
    _fill(_month(_project("Minit", vm)), catalog, wage="100")
    _fill(_month(_project("Europack", ds)), catalog, wage="50")

    grid = workbook_grid(YEAR, MONTH, offices=Office.objects.filter(pk=vm.pk))

    assert [c["project"].name for c in grid["columns"]] == ["Minit"]
    assert [o["office"] for o in grid["offices"]] == ["Velký Meder"]
    assert grid["grand"]["cost"] == Decimal("-100")


def test_a_project_opted_out_of_reporting_is_not_a_column(catalog):
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    kept = _project("Minit", office)
    opted_out = _project("Excluded", office, code="EXCL")
    opted_out.financial_reporting_eligible = False
    opted_out.save(update_fields=["financial_reporting_eligible"])
    _fill(_month(kept), catalog, wage="100")

    assert [c["project"].name for c in workbook_grid(YEAR, MONTH)["columns"]] == [
        "Minit"
    ]


# --- the year grid ---------------------------------------------------------


def test_the_year_grid_spreads_months_across(catalog):
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    project = _project("Minit", office)
    for month_number, wage in ((1, "100"), (2, "150"), (12, "200")):
        month = FinancialMonth.objects.create(
            project=project, year=YEAR, month=month_number
        )
        set_line_item(month, catalog["wage"], Decimal(wage))

    grid = project_year_grid(project, YEAR)
    wage_row = next(r for r in grid["rows"] if r["category"].label == "Gross wage")

    assert len(wage_row["months"]) == 12
    assert wage_row["months"][0] == Decimal("-100")
    assert wage_row["months"][1] == Decimal("-150")
    assert wage_row["months"][11] == Decimal("-200")
    assert wage_row["total"] == Decimal("-450")
    assert grid["year_total"]["cost"] == Decimal("-450")


def test_an_unrecorded_month_is_blank_not_zero(catalog):
    """A month nobody entered and a month that genuinely netted nothing are
    different facts, and the grid must not conflate them."""
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    project = _project("Minit", office)
    month = FinancialMonth.objects.create(project=project, year=YEAR, month=3)
    set_line_item(month, catalog["wage"], Decimal("100"))

    grid = project_year_grid(project, YEAR)
    wage_row = next(r for r in grid["rows"] if r["category"].label == "Gross wage")

    assert wage_row["months"][2] == Decimal("-100")
    assert wage_row["months"][0] is None
    assert grid["month_totals"][2]["recorded"] is True
    assert grid["month_totals"][0]["recorded"] is False


def test_the_year_grid_covers_only_its_own_year(catalog):
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    project = _project("Minit", office)
    for year in (YEAR, YEAR + 1):
        month = FinancialMonth.objects.create(project=project, year=year, month=5)
        set_line_item(month, catalog["wage"], Decimal("100"))

    assert project_year_grid(project, YEAR)["year_total"]["cost"] == Decimal("-100")


# --- the views -------------------------------------------------------------


@pytest.fixture
def manager(django_user_model):
    user = django_user_model.objects.create_user(
        email="fin-grid-mgr@demo.jober.test", password="x", role="manager"
    )
    return user


def test_the_year_view_refuses_another_offices_project(client, manager, catalog):
    """This view takes a project pk, so filtering some other list is not the
    boundary — the same reason `_assert_month_in_scope` exists."""
    from django.urls import reverse

    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    ds = Office.objects.create(name="Dunajská Streda", code="DS", country="SK")
    manager.offices.set([vm])
    theirs = _project("Europack", ds)
    client.force_login(manager)

    response = client.get(reverse("finance_project_year", args=[theirs.pk, YEAR]))

    assert response.status_code == 403


def test_the_year_view_allows_my_own_office(client, manager, catalog):
    from django.urls import reverse

    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    manager.offices.set([vm])
    mine = _project("Minit", vm)
    client.force_login(manager)

    response = client.get(reverse("finance_project_year", args=[mine.pk, YEAR]))

    assert response.status_code == 200


def test_the_workbook_view_shows_only_my_offices_columns(client, manager, catalog):
    from django.urls import reverse

    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    ds = Office.objects.create(name="Dunajská Streda", code="DS", country="SK")
    manager.offices.set([vm])
    _fill(_month(_project("Minit", vm)), catalog, wage="100")
    _fill(_month(_project("Europack", ds)), catalog, wage="50")
    client.force_login(manager)

    response = client.get(reverse("finance_workbook", args=[YEAR, MONTH]))

    assert response.status_code == 200
    grid = response.context["grid"]
    assert [c["project"].name for c in grid["columns"]] == ["Minit"]


def test_an_impossible_month_is_404_not_a_broken_grid(client, manager):
    from django.urls import reverse

    client.force_login(manager)
    assert client.get(reverse("finance_workbook", args=[YEAR, 13])).status_code == 404


def test_cells_land_in_the_right_column_when_ids_diverge(catalog):
    """Project ids and FinancialMonth ids are separate sequences.

    They coincide only on a freshly created database, so a lookup that confuses
    one for the other passes alone and fails in a shared run — which is exactly
    how this was found. Burning extra project rows first forces the two
    sequences apart, so the mix-up fails here every time instead of by luck.
    """
    office = Office.objects.create(name="Megyer", code="VM", country="SK")
    for n in range(4):  # consume project ids that no month will ever match
        _project(f"Filler {n}", office, code=f"FILL{n}")

    alpha = _project("Alpha", office, code="ALPHA")
    beta = _project("Beta", office, code="BETA")
    _fill(_month(alpha), catalog, wage="100")
    _fill(_month(beta), catalog, wage="900")

    grid = workbook_grid(YEAR, MONTH)
    wage_row = next(r for r in grid["cost_rows"] if r["category"].label == "Gross wage")
    by_name = dict(
        zip([c["project"].name for c in grid["columns"]], wage_row["values"])
    )

    assert by_name["Alpha"] == Decimal("-100")
    assert by_name["Beta"] == Decimal("-900")
