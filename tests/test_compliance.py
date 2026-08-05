from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse

from features.compliance.models import Certificate
from core.dates import add_months
from features.compliance.services import compliance_alerts
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project, ReadinessRecord

pytestmark = pytest.mark.django_db

TODAY = dt.date.today()


def test_add_months_clamps_day():
    assert add_months(dt.date(2026, 1, 31), 1) == dt.date(2026, 2, 28)
    assert add_months(dt.date(2026, 12, 15), 1) == dt.date(2027, 1, 15)


def test_working_person_missing_medical_is_flagged():
    Person.objects.create(
        first_name="A", last_name="B", lifecycle_status=LifecycleStatus.WORKING
    )
    alerts = compliance_alerts()
    assert any(a["item"] == "Medical" and a["severity"] == "missing" for a in alerts)


def test_expired_certificate_is_flagged():
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person, name="Forklift", expiry_date=TODAY - dt.timedelta(days=1)
    )
    alerts = compliance_alerts()
    assert any(a["item"] == "Forklift" and a["severity"] == "expired" for a in alerts)


def test_expiring_certificate_is_flagged():
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person, name="Visa", expiry_date=TODAY + dt.timedelta(days=10)
    )
    alerts = compliance_alerts()
    assert any(a["item"] == "Visa" and a["severity"] == "expiring" for a in alerts)


def test_far_future_certificate_not_flagged():
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person, name="Far", expiry_date=TODAY + dt.timedelta(days=400)
    )
    assert not any(a["item"] == "Far" for a in compliance_alerts())


def test_valid_recent_medical_not_flagged(settings):
    settings.MEDICAL_VALIDITY_MONTHS = 12
    project = Project.objects.create(name="DHL", code="DHLBA")
    person = Person.objects.create(
        first_name="A", last_name="B", lifecycle_status=LifecycleStatus.WORKING
    )
    ReadinessRecord.objects.create(
        person=person, project=project, entry_medical_date=TODAY
    )
    assert not any(a["item"] == "Medical" for a in compliance_alerts())


def test_compliance_page_requires_login(client):
    resp = client.get(reverse("compliance_list"))
    assert resp.status_code == 302
    assert reverse("login") in resp.headers["Location"]


def test_coordinator_sees_only_their_people(django_user_model):
    coord_a = django_user_model.objects.create_user(
        email="a@demo.jober.test", password="x", role="coordinator"
    )
    coord_b = django_user_model.objects.create_user(
        email="b@demo.jober.test", password="x", role="coordinator"
    )
    p1 = Project.objects.create(name="Alpha", code="ALPHA")
    p2 = Project.objects.create(name="Beta", code="BETA")
    p1.responsible_coordinators.add(coord_a)
    p2.responsible_coordinators.add(coord_b)
    from core.projects.services import activate_on_project

    alice = Person.objects.create(first_name="Alice", last_name="A")
    bob = Person.objects.create(first_name="Bob", last_name="B")
    activate_on_project(alice, p1, actor=coord_a)  # WORKING, no medical -> alert
    activate_on_project(bob, p2, actor=coord_b)

    names = {a["person"].first_name for a in compliance_alerts(coord_a)}
    assert "Alice" in names
    assert "Bob" not in names


# --- the medical is a date, and the product now chases it (2026-08-05) ------


def _worker_with_medical(status, medical_date, *, code="DHLBA"):
    project = Project.objects.get_or_create(name="DHL", code=code)[0]
    person = Person.objects.create(
        first_name="Fictional", last_name="Worker", lifecycle_status=status
    )
    ReadinessRecord.objects.create(
        person=person, project=project, entry_medical_date=medical_date
    )
    return person


def test_a_lapsed_medical_is_reported_for_someone_on_a_trial_day(settings):
    """A trial day happens on site. A lapsed medical there is worth saying."""
    settings.MEDICAL_VALIDITY_MONTHS = 12
    _worker_with_medical(LifecycleStatus.TRIAL_DAY, TODAY - dt.timedelta(days=400))

    alerts = compliance_alerts()

    assert any(a["item"] == "Medical" and a["severity"] == "expired" for a in alerts)


def test_a_candidate_with_no_medical_yet_is_not_a_compliance_failure():
    """Missing stays a working-person rule, or the real alerts get buried."""
    Person.objects.create(
        first_name="Fictional",
        last_name="Candidate",
        lifecycle_status=LifecycleStatus.TRIAL_DAY,
    )

    assert not any(a["item"] == "Medical" for a in compliance_alerts())


def test_an_inactive_person_with_a_lapsed_medical_is_left_alone(settings):
    settings.MEDICAL_VALIDITY_MONTHS = 12
    _worker_with_medical(LifecycleStatus.INACTIVE, TODAY - dt.timedelta(days=400))

    assert not any(a["item"] == "Medical" for a in compliance_alerts())


# --- the badge (features/compliance/panels.py) -----------------------------


def _badges(person, settings):
    from features.compliance.panels import certificate_badges

    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "documents": True}

    class _Request:
        user = None

    return certificate_badges(_Request(), person) or []


def test_a_recorded_medical_shows_as_a_badge(settings):
    settings.MEDICAL_VALIDITY_MONTHS = 12
    person = _worker_with_medical(LifecycleStatus.WORKING, TODAY)

    badges = _badges(person, settings)

    assert [b for b in badges if b["icon"] == "cert-health"]
    assert all(b["severity"] is None for b in badges)


def test_a_lapsed_medical_badge_carries_the_expired_severity(settings):
    settings.MEDICAL_VALIDITY_MONTHS = 12
    person = _worker_with_medical(
        LifecycleStatus.WORKING, TODAY - dt.timedelta(days=400)
    )

    health = [b for b in _badges(person, settings) if b["icon"] == "cert-health"]

    assert health and health[0]["severity"] == "expired"


def test_no_medical_date_means_no_health_badge(settings):
    person = Person.objects.create(first_name="Fictional", last_name="Worker")

    assert not [b for b in _badges(person, settings) if b["icon"] == "cert-health"]
