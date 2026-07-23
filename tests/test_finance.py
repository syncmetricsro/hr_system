from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.finance"):
    pytest.skip("features.finance is not installed for this client", allow_module_level=True)


from decimal import Decimal

import pytest

from core.accounts.permissions import Action, can
from features.finance.models import FinancialMonth
from features.finance.services import (
    FinanceError,
    company_totals,
    monthly_totals,
    record_financial_month,
)
from core.projects.models import Project

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup(django_user_model):
    actor = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    p1 = Project.objects.create(name="DHL", code="DHLBA")
    p2 = Project.objects.create(name="WEBASTO", code="WEB")
    return actor, p1, p2


def test_record_month_and_net(setup):
    actor, p1, _ = setup
    month = record_financial_month(p1, 2026, 5, "18000", "12000", actor=actor)
    assert month.net == Decimal("6000")


def test_company_totals_sum_all_projects(setup):
    actor, p1, p2 = setup
    record_financial_month(p1, 2026, 5, "18000", "12000", actor=actor)
    record_financial_month(p2, 2026, 5, "9000", "7000", actor=actor)
    totals = company_totals()
    assert totals["revenue"] == Decimal("27000")
    assert totals["cost"] == Decimal("19000")
    assert totals["net"] == Decimal("8000")


def test_idempotent_per_project_month(setup):
    actor, p1, _ = setup
    record_financial_month(p1, 2026, 5, "10000", "5000", actor=actor)
    record_financial_month(p1, 2026, 5, "11000", "5000", actor=actor)
    assert FinancialMonth.objects.filter(project=p1, year=2026, month=5).count() == 1


def test_locked_month_rejected(setup):
    actor, p1, _ = setup
    m = record_financial_month(p1, 2026, 5, "10000", "5000", actor=actor)
    m.is_locked = True
    m.save(update_fields=["is_locked"])
    with pytest.raises(FinanceError):
        record_financial_month(p1, 2026, 5, "12000", "5000", actor=actor)


def test_monthly_totals_aggregates_across_projects(setup):
    actor, p1, p2 = setup
    record_financial_month(p1, 2026, 5, "18000", "12000", actor=actor)
    record_financial_month(p2, 2026, 5, "9000", "7000", actor=actor)
    record_financial_month(p1, 2026, 6, "10000", "4000", actor=actor)
    rows = monthly_totals()
    assert len(rows) == 2
    may = next(r for r in rows if r["month"] == 5)
    assert may["year"] == 2026
    assert may["revenue"] == Decimal("27000")
    assert may["cost"] == Decimal("19000")
    assert may["net"] == Decimal("8000")


def test_monthly_totals_is_ascending_unlike_yearly_totals(setup):
    actor, p1, _ = setup
    record_financial_month(p1, 2026, 6, "1000", "500", actor=actor)
    record_financial_month(p1, 2025, 12, "1000", "500", actor=actor)
    rows = monthly_totals()
    assert [(r["year"], r["month"]) for r in rows] == [(2025, 12), (2026, 6)]


def test_monthly_totals_excludes_ineligible_projects(setup):
    actor, p1, p2 = setup
    p2.financial_reporting_eligible = False
    p2.save(update_fields=["financial_reporting_eligible"])
    record_financial_month(p1, 2026, 5, "18000", "12000", actor=actor)
    record_financial_month(p2, 2026, 5, "9000", "7000", actor=actor)
    rows = monthly_totals()
    assert len(rows) == 1
    assert rows[0]["revenue"] == Decimal("18000")


def test_monthly_totals_scoped_to_year(setup):
    actor, p1, _ = setup
    record_financial_month(p1, 2025, 12, "1000", "500", actor=actor)
    record_financial_month(p1, 2026, 1, "2000", "500", actor=actor)
    rows = monthly_totals(year=2026)
    assert len(rows) == 1
    assert rows[0]["month"] == 1


def test_monthly_totals_all_locked_true_only_when_every_row_locked(setup):
    actor, p1, p2 = setup
    m1 = record_financial_month(p1, 2026, 5, "18000", "12000", actor=actor)
    record_financial_month(p2, 2026, 5, "9000", "7000", actor=actor)
    rows = monthly_totals()
    assert rows[0]["all_locked"] is False

    m1.is_locked = True
    m1.save(update_fields=["is_locked"])
    rows = monthly_totals()
    assert rows[0]["all_locked"] is False

    FinancialMonth.objects.filter(year=2026, month=5).update(is_locked=True)
    rows = monthly_totals()
    assert rows[0]["all_locked"] is True


def test_finance_rbac(django_user_model):
    manager = django_user_model.objects.create_user(email="m2@demo.jober.test", password="x", role="manager")
    observer = django_user_model.objects.create_user(email="o@demo.jober.test", password="x", role="observer")
    recruiter = django_user_model.objects.create_user(email="r@demo.jober.test", password="x", role="recruiter")
    assert can(manager, Action.FINANCE_MANAGE)
    assert not can(observer, Action.FINANCE_MANAGE)
    assert can(observer, Action.FINANCE_VIEW_SUMMARY)
    assert not can(recruiter, Action.FINANCE_VIEW_SUMMARY)
