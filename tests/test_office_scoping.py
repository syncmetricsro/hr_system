from __future__ import annotations

import re
import json
from decimal import Decimal

import pytest
from django.apps import apps as django_apps
from django.urls import reverse

if not django_apps.is_installed("features.profitability"):
    pytest.skip("features.profitability is not installed for this client", allow_module_level=True)

from core.accounts.permissions import user_office_scope
from core.offices.models import Office
from core.projects.models import Project
from features.profitability.services import record_financial_month

pytestmark = pytest.mark.django_db


def extract_json_script(html: str, element_id: str) -> dict:
    match = re.search(
        rf'<script id="{re.escape(element_id)}" type="application/json">(.*?)</script>',
        html, re.DOTALL,
    )
    assert match, f"json_script #{element_id} not found in response"
    return json.loads(match.group(1))


@pytest.fixture
def two_offices(django_user_model):
    # Office seeding is Jober-only (clients/jober/demo/management/commands/
    # seed_people.py), not a core migration - the test DB starts with no
    # offices at all, so create our own here.
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    observer = django_user_model.objects.create_user(
        email="obs@demo.jober.test", password="x", role="observer"
    )

    p_vm = Project.objects.create(name="VM Project", code="VMPROJ", office=velky_meder)
    p_gyr = Project.objects.create(name="Győr Project", code="GYRPROJ", office=gyor)
    record_financial_month(p_vm, 2026, 5, "10000", "6000", actor=manager)
    record_financial_month(p_gyr, 2026, 5, "20000", "5000", actor=manager)
    return {
        "velky_meder": velky_meder, "gyor": gyor,
        "manager": manager, "observer": observer,
        "p_vm": p_vm, "p_gyr": p_gyr,
    }


def test_user_office_scope_observer_is_unrestricted(two_offices):
    assert user_office_scope(two_offices["observer"]) is None


def test_user_office_scope_manager_is_their_offices_only(two_offices):
    scope = user_office_scope(two_offices["manager"])
    assert list(scope) == [two_offices["velky_meder"]]


def test_manager_finance_page_shows_only_their_office(client, two_offices):
    from features.profitability.services import company_totals

    client.force_login(two_offices["manager"])
    resp = client.get(reverse("finance_summary"))
    body = resp.content.decode()

    assert "Velký Meder" in body
    assert "Győr" not in body
    # The view's own scoped total (not just the page text) is office-only.
    scope = user_office_scope(two_offices["manager"])
    assert company_totals(offices=scope) == {
        "revenue": Decimal("10000"), "cost": Decimal("6000"), "net": Decimal("4000"),
    }


def test_observer_gets_executive_page_with_all_offices(client, two_offices):
    client.force_login(two_offices["observer"])
    body = client.get(reverse("finance_summary")).content.decode()

    assert "Velký Meder" in body
    assert "Győr" in body

    trend = extract_json_script(body, "chart-data-finance-executive-trend")
    office_labels = {series["label"] for series in trend["series"]}
    assert office_labels == {"Velký Meder", "Győr"}


def test_manager_cannot_view_another_offices_month_detail(client, two_offices):
    from features.profitability.models import FinancialMonth

    client.force_login(two_offices["manager"])
    other_month = FinancialMonth.objects.get(project=two_offices["p_gyr"], year=2026, month=5)
    resp = client.get(reverse("finance_month_detail", args=[other_month.pk]))
    assert resp.status_code == 403


def test_manager_can_view_their_own_offices_month_detail(client, two_offices):
    from features.profitability.models import FinancialMonth

    client.force_login(two_offices["manager"])
    own_month = FinancialMonth.objects.get(project=two_offices["p_vm"], year=2026, month=5)
    resp = client.get(reverse("finance_month_detail", args=[own_month.pk]))
    assert resp.status_code == 200


def test_manager_cannot_record_month_for_another_offices_project(client, two_offices):
    client.force_login(two_offices["manager"])
    resp = client.post(reverse("finance_record"), {
        "project": two_offices["p_gyr"].pk,
        "year": "2026", "month": "6", "revenue": "1000", "cost": "500",
    })
    assert resp.status_code == 403


def test_observer_can_view_any_offices_month_detail(client, two_offices):
    from features.profitability.models import FinancialMonth

    client.force_login(two_offices["observer"])
    month = FinancialMonth.objects.get(project=two_offices["p_gyr"], year=2026, month=5)
    resp = client.get(reverse("finance_month_detail", args=[month.pk]))
    assert resp.status_code == 200


def test_office_totals_offices_none_returns_unfiltered_including_no_office_project(two_offices):
    """offices=None must mean genuinely unfiltered, not 'all offices' - a
    project with no office assigned at all must still show for the Observer."""
    from features.profitability.services import office_totals

    unassigned_project = Project.objects.create(name="No Office Yet", code="NOOFF")
    record_financial_month(unassigned_project, 2026, 5, "500", "100", actor=two_offices["manager"])

    totals = office_totals(2026, offices=None)
    labels = {row["office"] for row in totals}
    assert "Unassigned" in labels
