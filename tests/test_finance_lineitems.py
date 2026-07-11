from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.finance"):
    pytest.skip("features.finance is not installed for this client", allow_module_level=True)


from decimal import Decimal

import pytest
from django.urls import reverse

from features.finance.models import (
    FinanceCategory,
    FinanceCategoryKind,
    FinanceGroup,
    FinancialMonth,
)
from features.finance.services import (
    FinanceError,
    company_totals,
    group_breakdown,
    lock_month,
    project_totals,
    recompute_month,
    reopen_month,
    set_line_item,
    yearly_totals,
)
from core.projects.models import Project

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    actor = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    project = Project.objects.create(name="DHL", code="DHLBA")
    month = FinancialMonth.objects.create(project=project, year=2026, month=5)
    wage = FinanceCategory.objects.create(
        label="Gross wage", kind=FinanceCategoryKind.COST, group=FinanceGroup.LABOUR
    )
    fuel = FinanceCategory.objects.create(
        label="Fuel", kind=FinanceCategoryKind.COST, group=FinanceGroup.TRANSPORT
    )
    invoice = FinanceCategory.objects.create(
        label="Client invoices", kind=FinanceCategoryKind.REVENUE, group=FinanceGroup.REVENUE
    )
    return actor, month, wage, fuel, invoice


def test_recompute_sums_by_kind(setup):
    actor, month, wage, fuel, invoice = setup
    set_line_item(month, wage, "12000", actor=actor)
    set_line_item(month, fuel, "800", actor=actor)
    set_line_item(month, invoice, "18000", actor=actor)
    recompute_month(month, actor=actor)
    month.refresh_from_db()
    assert month.cost == Decimal("12800")
    assert month.revenue == Decimal("18000")
    assert month.net == Decimal("5200")


def test_recompute_dynamic_covers_all_rows(setup):
    """Every cost row counts — guards against the spreadsheet's off-by-one bug."""
    actor, month, wage, fuel, invoice = setup
    extra = FinanceCategory.objects.create(
        label="Toll", kind=FinanceCategoryKind.COST, group=FinanceGroup.TRANSPORT
    )
    for cat, amt in [(wage, "100"), (fuel, "100"), (extra, "100")]:
        set_line_item(month, cat, amt, actor=actor)
    recompute_month(month, actor=actor)
    month.refresh_from_db()
    assert month.cost == Decimal("300")  # last row not dropped


def test_set_line_item_updates_in_place(setup):
    actor, month, wage, *_ = setup
    set_line_item(month, wage, "100", actor=actor)
    set_line_item(month, wage, "250", actor=actor)
    assert month.line_items.filter(category=wage).count() == 1
    assert month.line_items.get(category=wage).amount == Decimal("250")


def test_locked_month_blocks_edits(setup):
    actor, month, wage, *_ = setup
    month.is_locked = True
    month.save(update_fields=["is_locked"])
    with pytest.raises(FinanceError):
        set_line_item(month, wage, "100", actor=actor)
    with pytest.raises(FinanceError):
        recompute_month(month, actor=actor)


def test_group_breakdown_nets_revenue_minus_cost(setup):
    actor, month, wage, fuel, invoice = setup
    accom_cost = FinanceCategory.objects.create(
        label="Accommodation", kind=FinanceCategoryKind.COST, group=FinanceGroup.ACCOMMODATION
    )
    accom_rev = FinanceCategory.objects.create(
        label="Accommodation charged", kind=FinanceCategoryKind.REVENUE, group=FinanceGroup.ACCOMMODATION
    )
    set_line_item(month, accom_cost, "1000", actor=actor)
    set_line_item(month, accom_rev, "1500", actor=actor)
    set_line_item(month, wage, "12000", actor=actor)
    rows = {r["group"]: r for r in group_breakdown([month])}
    assert rows[FinanceGroup.ACCOMMODATION]["net"] == Decimal("500")
    assert rows[FinanceGroup.LABOUR]["net"] == Decimal("-12000")


def test_save_view_persists_and_recomputes(client, setup):
    actor, month, wage, fuel, invoice = setup
    client.force_login(actor)
    resp = client.post(
        reverse("finance_month_save", kwargs={"pk": month.pk}),
        {f"cat_{wage.pk}": "12000", f"cat_{invoice.pk}": "18000"},
    )
    assert resp.status_code == 302
    month.refresh_from_db()
    assert month.cost == Decimal("12000")
    assert month.revenue == Decimal("18000")


def test_detail_view_gated_to_internal(client, setup, django_user_model):
    _actor, month, *_ = setup
    recruiter = django_user_model.objects.create_user(
        email="r@demo.jober.test", password="x", role="recruiter"
    )
    client.force_login(recruiter)
    resp = client.get(reverse("finance_month_detail", kwargs={"pk": month.pk}))
    assert resp.status_code == 403  # recruiters cannot view finance summary


def test_lock_then_reopen_requires_reason(setup):
    actor, month, wage, *_ = setup
    lock_month(month, actor=actor)
    month.refresh_from_db()
    assert month.is_locked
    with pytest.raises(FinanceError):
        set_line_item(month, wage, "100", actor=actor)
    with pytest.raises(FinanceError):
        reopen_month(month, reason="   ", actor=actor)  # blank reason rejected
    reopen_month(month, reason="Late invoice correction", actor=actor)
    month.refresh_from_db()
    assert not month.is_locked
    set_line_item(month, wage, "100", actor=actor)  # editable again


def test_reopen_audits_reason(setup, django_user_model):
    from core.audit.models import AuditEvent

    actor, month, *_ = setup
    lock_month(month, actor=actor)
    reopen_month(month, reason="Client adjustment", actor=actor)
    event = AuditEvent.objects.filter(action="finance.reopened").latest("created_at")
    assert event.reason == "Client adjustment"


def test_lock_view_blocks_save(client, setup):
    actor, month, wage, fuel, invoice = setup
    lock_month(month, actor=actor)
    client.force_login(actor)
    resp = client.post(
        reverse("finance_month_save", kwargs={"pk": month.pk}),
        {f"cat_{wage.pk}": "999"},
    )
    assert resp.status_code == 302
    assert not month.line_items.filter(category=wage).exists()  # locked: nothing written


def test_project_and_yearly_totals(setup):
    actor, month, wage, fuel, invoice = setup
    set_line_item(month, invoice, "18000", actor=actor)
    set_line_item(month, wage, "12000", actor=actor)
    recompute_month(month, actor=actor)
    projects = project_totals()
    assert projects[0]["net"] == Decimal("6000")
    assert project_totals(2026)[0]["net"] == Decimal("6000")
    assert project_totals(2099) == []
    years = yearly_totals()
    assert years[0]["year"] == 2026
    assert years[0]["net"] == Decimal("6000")
    assert company_totals(2026)["net"] == Decimal("6000")
    assert company_totals(2099)["net"] == Decimal("0")
