from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.finance"):
    pytest.skip("features.finance is not installed for this client", allow_module_level=True)


from decimal import Decimal

import pytest

from core.accounts.permissions import Action, can
from features.finance.models import FinancialMonth
from features.finance.services import FinanceError, company_totals, record_financial_month
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


def test_finance_rbac(django_user_model):
    manager = django_user_model.objects.create_user(email="m2@demo.jober.test", password="x", role="manager")
    observer = django_user_model.objects.create_user(email="o@demo.jober.test", password="x", role="observer")
    recruiter = django_user_model.objects.create_user(email="r@demo.jober.test", password="x", role="recruiter")
    assert can(manager, Action.FINANCE_MANAGE)
    assert not can(observer, Action.FINANCE_MANAGE)
    assert can(observer, Action.FINANCE_VIEW_SUMMARY)
    assert not can(recruiter, Action.FINANCE_VIEW_SUMMARY)
