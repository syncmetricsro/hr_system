from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.urls import reverse
from django.utils import translation

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
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def finance_users(django_user_model):
    office = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    other_office = Office.objects.create(name="Győr", code="GYR", country="HU")
    manager = django_user_model.objects.create_user(
        email="empty-finance-manager@demo.jober.test",
        password="x",
        role="manager",
    )
    manager.offices.set([office])
    observer = django_user_model.objects.create_user(
        email="empty-finance-observer@demo.jober.test",
        password="x",
        role="observer",
    )
    return manager, observer, office, other_office


def _english_body(response):
    return response.content.decode("utf-8")


def test_empty_summary_explains_project_prerequisite_and_links_manager(
    client, finance_users
):
    manager, _observer, _office, _other_office = finance_users
    client.force_login(manager)

    with translation.override("en"):
        project_create_url = reverse("project_create")
        response = client.get(reverse("finance_summary"))

    body = _english_body(response)
    assert response.status_code == 200
    assert "Create a finance-enabled project first" in body
    assert project_create_url in body
    assert "there are no project columns or year grids" in body


def test_empty_workbook_is_explanatory_and_hides_unauthorized_action(
    client, finance_users
):
    _manager, observer, _office, _other_office = finance_users
    client.force_login(observer)

    with translation.override("en"):
        project_create_url = reverse("project_create")
        response = client.get(reverse("finance_workbook", args=[2026, 8]))

    body = _english_body(response)
    assert response.status_code == 200
    assert "This workbook cannot be edited" in body
    assert "Create a finance-enabled project first" in body
    assert project_create_url not in body
    assert '<table class="data-table workbook-grid">' not in body


def test_empty_workbook_guidance_is_translated_in_hungarian(client, finance_users):
    manager, _observer, _office, _other_office = finance_users
    client.force_login(manager)

    with translation.override("hu"):
        response = client.get(reverse("finance_workbook", args=[2026, 8]))

    body = _english_body(response)
    assert "Először hozzon létre egy Pénzügyekben szereplő projektet" in body
    assert "Create a finance-enabled project first" not in body


def test_year_lists_scoped_eligible_projects_before_any_month_exists(
    client, finance_users
):
    manager, _observer, office, other_office = finance_users
    included = Project.objects.create(name="Minit", code="MINIT", office=office)
    Project.objects.create(
        name="Hidden",
        code="HIDDEN",
        office=office,
        financial_reporting_eligible=False,
    )
    Project.objects.create(name="Other office", code="OTHER", office=other_office)
    Project.objects.create(
        name="Inactive", code="INACTIVE", office=office, is_active=False
    )
    client.force_login(manager)

    with translation.override("en"):
        year_url = reverse("finance_project_year", args=[included.pk, 2026])
        response = client.get(reverse("finance_year", args=[2026]))

    body = _english_body(response)
    assert year_url in body
    assert "Hidden" not in body
    assert "Other office" not in body
    assert "Inactive" not in body


def test_blank_project_year_explains_that_save_creates_months(client, finance_users):
    manager, _observer, office, _other_office = finance_users
    project = Project.objects.create(name="Minit", code="MINIT", office=office)
    FinanceCategory.objects.create(label="Gross wage", kind=FinanceCategoryKind.COST)
    client.force_login(manager)

    with translation.override("en"):
        response = client.get(reverse("finance_project_year", args=[project.pk, 2026]))

    body = _english_body(response)
    assert "Blank cells are expected" in body
    assert "creates the corresponding monthly record" in body
    assert "Save year" in body


def test_project_year_reports_a_missing_category_catalogue(client, finance_users):
    manager, _observer, office, _other_office = finance_users
    project = Project.objects.create(name="Minit", code="MINIT", office=office)
    client.force_login(manager)

    with translation.override("en"):
        response = client.get(reverse("finance_project_year", args=[project.pk, 2026]))

    assert "Finance categories are missing" in _english_body(response)
