from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.people.models import LifecycleStatus, Person
from core.projects.models import Project

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_user(django_user_model):
    def _make(role):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )
    return _make


def test_reports_requires_login(client):
    resp = client.get(reverse("reports"))
    assert resp.status_code == 302
    assert reverse("login") in resp.headers["Location"]


def test_reports_shows_counts(client, make_user):
    Project.objects.create(name="DHL", code="DHLBA")
    Person.objects.create(first_name="A", last_name="B", lifecycle_status=LifecycleStatus.AVAILABLE)
    client.force_login(make_user("manager"))
    with translation.override("sk"):
        body = client.get(reverse("reports")).content.decode("utf-8")
    assert "Reporty" in body                    # heading (sk)
    assert "Ľudia podľa stavu" in body          # people-by-status section
    assert 'href="/sk/projects/"' in body
    assert 'href="/sk/people/?status=available"' in body


@pytest.mark.jober_only
def test_manager_report_tiles_link_to_their_operational_drill_downs(client, make_user):
    client.force_login(make_user("manager"))
    body = client.get(reverse("reports")).content.decode("utf-8")

    assert f'href="{reverse("accommodation_costs")}"' in body
    assert f'href="{reverse("equipment_reviews")}"' in body
    assert f'href="{reverse("compliance_list")}"' in body


def test_finance_section_hidden_from_recruiter(client, make_user):
    client.force_login(make_user("recruiter"))
    with translation.override("sk"):
        body = client.get(reverse("reports")).content.decode("utf-8")
    # Finance section heading should not appear for a role without finance.view_summary
    assert "Celkový súčet firmy" not in body


@pytest.mark.jober_only  # Jober grants/lifecycle/features
def test_finance_section_visible_to_observer(client, make_user):
    client.force_login(make_user("observer"))
    with translation.override("sk"):
        body = client.get(reverse("reports")).content.decode("utf-8")
    assert "Celkový súčet firmy" in body
