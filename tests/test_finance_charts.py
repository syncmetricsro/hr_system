from __future__ import annotations

import json
import re
from decimal import Decimal

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.finance"):
    pytest.skip("features.finance is not installed for this client", allow_module_level=True)


from django.urls import reverse

from features.finance.models import FinanceCategory, FinanceCategoryKind, FinanceGroup, FinancialMonth
from features.finance.services import record_financial_month, set_line_item
from core.projects.models import Project

pytestmark = pytest.mark.django_db


def extract_json_script(html: str, element_id: str) -> dict:
    match = re.search(
        rf'<script id="{re.escape(element_id)}" type="application/json">(.*?)</script>',
        html, re.DOTALL,
    )
    assert match, f"json_script #{element_id} not found in response"
    return json.loads(match.group(1))


@pytest.fixture
def setup(django_user_model):
    actor = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    p1 = Project.objects.create(name="DHL", code="DHLBA")
    p2 = Project.objects.create(name="WEBASTO", code="WEB")
    month1 = record_financial_month(p1, 2026, 5, "18000", "12000", actor=actor)
    record_financial_month(p2, 2026, 5, "9000", "7000", actor=actor)
    wage = FinanceCategory.objects.create(
        label="Gross wage", kind=FinanceCategoryKind.COST, group=FinanceGroup.LABOUR
    )
    invoice = FinanceCategory.objects.create(
        label="Client invoices", kind=FinanceCategoryKind.REVENUE, group=FinanceGroup.REVENUE
    )
    set_line_item(month1, wage, "12000", actor=actor)
    set_line_item(month1, invoice, "18000", actor=actor)
    return actor, p1, p2


def test_finance_summary_renders_expected_canvases_and_trend_data(client, setup):
    actor, *_ = setup
    client.force_login(actor)
    body = client.get(reverse("finance_summary")).content.decode()

    assert 'data-chart="trend"' in body
    assert 'data-chart="gauge"' in body
    assert 'data-chart="diverging"' in body

    trend = extract_json_script(body, "chart-data-finance-summary-trend")
    assert trend["labels"] == ["2026-05"]
    assert Decimal(trend["revenue"][0]) == Decimal("27000")
    assert Decimal(trend["cost"][0]) == Decimal("-19000")
    assert Decimal(trend["net"][0]) == Decimal("8000")

    gauge = extract_json_script(body, "chart-data-finance-summary-gauge")
    assert Decimal(gauge["margin_pct"]) == (Decimal("8000") / Decimal("27000") * 100).quantize(Decimal("0.1"))

    group = extract_json_script(body, "chart-data-finance-summary-group")
    assert "labels" in group and "net" in group


def test_finance_year_renders_trend_and_project_charts(client, setup):
    actor, *_ = setup
    client.force_login(actor)
    body = client.get(reverse("finance_year", args=[2026])).content.decode()

    assert 'data-chart="trend"' in body
    assert 'data-chart="diverging"' in body

    project_chart = extract_json_script(body, "chart-data-finance-year-project")
    assert set(project_chart["labels"]) == {"DHL", "WEBASTO"}


def test_finance_year_omits_trend_chart_when_no_months(client, django_user_model):
    manager = django_user_model.objects.create_user(
        email="empty@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)
    body = client.get(reverse("finance_year", args=[2099])).content.decode()
    assert 'data-chart="trend"' not in body


def test_finance_month_detail_renders_group_chart(client, setup):
    actor, p1, _ = setup
    client.force_login(actor)
    month = FinancialMonth.objects.get(project=p1, year=2026, month=5)
    body = client.get(reverse("finance_month_detail", args=[month.pk])).content.decode()

    assert 'data-chart="diverging"' in body
    group = extract_json_script(body, "chart-data-finance-month-group")
    assert "labels" in group and "net" in group
