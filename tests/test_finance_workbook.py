from __future__ import annotations

from decimal import Decimal

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.finance"):
    pytest.skip("features.finance is not installed for this client", allow_module_level=True)

from core.projects.models import Project
from features.finance.models import FinanceCategory, FinanceCategoryKind, FinancialMonth
from features.finance.services import (
    FinanceError, normalize_source_amount, recompute_month, regional_totals, set_line_item,
)

pytestmark = pytest.mark.django_db


def test_workbook_sign_validation_and_positive_storage():
    assert normalize_source_amount(FinanceCategoryKind.COST, "-200") == Decimal("200")
    assert normalize_source_amount(FinanceCategoryKind.REVENUE, "300") == Decimal("300")
    with pytest.raises(FinanceError):
        normalize_source_amount(FinanceCategoryKind.COST, "200")
    with pytest.raises(FinanceError):
        normalize_source_amount(FinanceCategoryKind.REVENUE, "-300")


def test_regional_totals_include_extraordinary_row_and_skip_opt_out():
    included = Project.objects.create(name="Minit demo", code="MINIT", region="Megyer")
    excluded = Project.objects.create(
        name="Opt out", code="OFF", region="Megyer", financial_reporting_eligible=False
    )
    cost = FinanceCategory.objects.create(label="Base cost", kind=FinanceCategoryKind.COST)
    extra = FinanceCategory.objects.create(label="Extraordinary", kind=FinanceCategoryKind.COST)
    revenue = FinanceCategory.objects.create(label="Invoices", kind=FinanceCategoryKind.REVENUE)
    month = FinancialMonth.objects.create(project=included, year=2025, month=11)
    for category, amount in ((cost, "1000"), (extra, "200"), (revenue, "2000")):
        set_line_item(month, category, amount)
    recompute_month(month)
    FinancialMonth.objects.create(project=excluded, year=2025, month=11, revenue=9999)
    assert regional_totals(2025) == [{
        "region": "Megyer", "revenue": Decimal("2000"),
        "cost": Decimal("-1200"), "net": Decimal("800"),
    }]
