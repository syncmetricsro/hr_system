from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import translation

from core.people.models import LifecycleStatus, Person
from core.ui.registry import nav_badge as registry_nav_badge
from core.ui.registry import person_badges as registry_person_badges
from core.ui.templatetags.avatars import status_pill
from features.compliance.models import Certificate, CertificateCategory
from features.compliance.panels import certificate_badges, compliance_badge
from features.compliance.services import most_relevant_certificate
from features.logistics.models import EquipmentItem
from features.logistics.panels import reviews_badge
from features.logistics.services import flag_unreturned, issue_equipment, receive_stock

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_user(django_user_model):
    def _make(role, email=None):
        return django_user_model.objects.create_user(
            email=email or f"{role}@demo.jober.test", password="x", role=role
        )

    return _make


# --- {% status_pill %} tag ---------------------------------------------------


@pytest.mark.parametrize(
    ("status", "tone"),
    [
        (LifecycleStatus.WORKING, "success"),
        (LifecycleStatus.TRIAL_DAY, "warning"),
        (LifecycleStatus.AVAILABLE, "info"),
        (LifecycleStatus.INACTIVE, "neutral"),
        (LifecycleStatus.BLACKLISTED, "danger"),
    ],
)
def test_status_pill_dot_uses_correct_tone(status, tone):
    person = Person(first_name="A", last_name="B", lifecycle_status=status)
    html = status_pill(person, size="dot")
    assert f"status-pill-{tone}" in html
    assert "status-pill-dot" in html


def test_status_pill_label_shows_visible_text():
    person = Person(
        first_name="A", last_name="B", lifecycle_status=LifecycleStatus.WORKING
    )
    with translation.override("en"):
        html = status_pill(person, size="label")
    assert "status-pill-label" in html
    assert "Working" in html


# --- Nav badge registry + providers ------------------------------------------


def test_compliance_badge_none_when_no_alerts(client, make_user):
    manager = make_user("manager")
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    assert compliance_badge(request) is None


def test_compliance_badge_counts_alerts_and_flags_severe(client, make_user):
    manager = make_user("manager")
    Person.objects.create(
        first_name="A", last_name="B", lifecycle_status=LifecycleStatus.WORKING
    )
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    result = compliance_badge(request)
    assert result == {"count": 1, "severe": True}  # missing medical -> severe


def test_compliance_badge_amber_when_only_expiring(client, make_user):
    manager = make_user("manager")
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person, name="Visa", expiry_date=date.today() + timedelta(days=10)
    )
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    result = compliance_badge(request)
    assert result == {"count": 1, "severe": False}


def test_compliance_badge_none_for_anonymous(client):
    request = client.get(reverse("login")).wsgi_request
    assert compliance_badge(request) is None


def test_reviews_badge_none_when_no_pending_reviews(client, make_user):
    manager = make_user("manager")
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    assert reviews_badge(request) is None


def test_reviews_badge_counts_pending_and_gated_by_rbac(client, make_user):
    manager = make_user("manager")
    coordinator = make_user("coordinator", email="c@demo.jober.test")
    item = EquipmentItem.objects.create(
        name="Boots", size="42", unit_price=Decimal("45.00")
    )
    receive_stock(
        received_on=date.today(),
        operation_key=uuid4(),
        lines=[{"item": item, "quantity": 5, "total_value": Decimal("225.00")}],
        actor=manager,
    )
    person = Person.objects.create(first_name="A", last_name="B")
    issue = issue_equipment(person, item, 1, actor=manager, operation_key=uuid4())
    flag_unreturned(issue, actor=manager)

    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    assert reviews_badge(request) == {"count": 1, "severe": False}

    request.user = coordinator
    assert (
        reviews_badge(request) is None
    )  # coordinator lacks equipment.review_deduction


def test_nav_badge_registry_returns_first_non_none_provider():
    from core.ui.registry import register_nav_badge

    register_nav_badge("_test_slot", lambda request: None, order=10)
    register_nav_badge(
        "_test_slot", lambda request: {"count": 3, "severe": True}, order=20
    )
    assert registry_nav_badge(object(), "_test_slot") == {"count": 3, "severe": True}


def test_nav_badge_registry_returns_none_for_unknown_slot():
    assert registry_nav_badge(object(), "_no_such_slot") is None


# --- End-to-end rendering -----------------------------------------------------


def test_person_detail_renders_status_pill(client, make_user):
    manager = make_user("manager")
    person = Person.objects.create(
        first_name="A", last_name="B", lifecycle_status=LifecycleStatus.WORKING
    )
    client.force_login(manager)
    resp = client.get(reverse("person_detail", args=[person.pk]))
    assert resp.status_code == 200
    assert b"status-pill-success" in resp.content


def test_people_list_renders_status_pill_dot(client, make_user):
    manager = make_user("manager")
    Person.objects.create(
        first_name="A", last_name="B", lifecycle_status=LifecycleStatus.BLACKLISTED
    )
    client.force_login(manager)
    resp = client.get(reverse("people_list"))
    assert resp.status_code == 200
    assert b"status-pill-danger" in resp.content
    assert b"status-pill-dot" in resp.content


def test_nav_shows_compliance_badge_when_alerts_exist(client, make_user):
    manager = make_user("manager")
    Person.objects.create(
        first_name="A", last_name="B", lifecycle_status=LifecycleStatus.WORKING
    )
    client.force_login(manager)
    resp = client.get(reverse("people_list"))
    assert b'notification-count-alert">1</span>' in resp.content


def test_nav_hides_compliance_badge_when_no_alerts(client, make_user):
    manager = make_user("manager")
    client.force_login(manager)
    resp = client.get(reverse("people_list"))
    body = resp.content.decode()
    assert "notification-count-alert" not in body
    assert "notification-count-warning" not in body


def test_anonymous_login_page_renders_without_badge_or_db_error(client):
    resp = client.get(reverse("login"))
    assert resp.status_code == 200
    assert b"notification-count" not in resp.content


# --- Certificate-validity icons (pill-system-design.md §2, Phase 2) --------

TODAY = date.today()


def test_most_relevant_certificate_prefers_soonest_expiring_valid():
    person = Person.objects.create(first_name="A", last_name="B")
    soon = Certificate.objects.create(
        person=person, name="Soon", expiry_date=TODAY + timedelta(days=5)
    )
    later = Certificate.objects.create(
        person=person, name="Later", expiry_date=TODAY + timedelta(days=100)
    )
    assert most_relevant_certificate([soon, later], TODAY) == soon


def test_most_relevant_certificate_falls_back_to_most_expired_when_none_valid():
    person = Person.objects.create(first_name="A", last_name="B")
    long_expired = Certificate.objects.create(
        person=person, name="Old", expiry_date=TODAY - timedelta(days=100)
    )
    recently_expired = Certificate.objects.create(
        person=person, name="Recent", expiry_date=TODAY - timedelta(days=5)
    )
    assert (
        most_relevant_certificate([long_expired, recently_expired], TODAY)
        == long_expired
    )


def test_most_relevant_certificate_treats_no_expiry_as_valid_but_never_urgent():
    person = Person.objects.create(first_name="A", last_name="B")
    evergreen = Certificate.objects.create(
        person=person, name="No expiry", expiry_date=None
    )
    soon = Certificate.objects.create(
        person=person, name="Soon", expiry_date=TODAY + timedelta(days=5)
    )
    assert most_relevant_certificate([evergreen], TODAY) == evergreen
    assert most_relevant_certificate([evergreen, soon], TODAY) == soon


def test_certificate_badges_none_when_no_certificates(client, make_user):
    manager = make_user("manager")
    person = Person.objects.create(first_name="A", last_name="B")
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    assert certificate_badges(request, person) is None


def test_certificate_badges_groups_by_category_and_tints_by_severity(client, make_user):
    manager = make_user("manager")
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person,
        name="Forklift",
        category=CertificateCategory.FORKLIFT,
        expiry_date=TODAY - timedelta(days=1),
    )
    Certificate.objects.create(
        person=person,
        name="Health check",
        category=CertificateCategory.HEALTH,
        expiry_date=TODAY + timedelta(days=400),
    )
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    badges = certificate_badges(request, person)
    by_icon = {b["icon"]: b for b in badges}
    assert by_icon["cert-forklift"]["severity"] == "expired"
    assert by_icon["cert-health"]["severity"] is None


def test_certificate_badges_picks_most_relevant_row_per_category(client, make_user):
    manager = make_user("manager")
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person,
        name="Old forklift",
        category=CertificateCategory.FORKLIFT,
        expiry_date=TODAY - timedelta(days=100),
    )
    Certificate.objects.create(
        person=person,
        name="Renewed forklift",
        category=CertificateCategory.FORKLIFT,
        expiry_date=TODAY + timedelta(days=100),
    )
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager
    badges = certificate_badges(request, person)
    assert len(badges) == 1
    assert "Renewed forklift" in badges[0]["tooltip"]


def test_register_person_badges_and_getter(monkeypatch):
    import core.ui.registry as registry_module

    monkeypatch.setattr(registry_module, "_person_badges", [])
    person = Person.objects.create(first_name="A", last_name="B")

    registry_module.register_person_badges(lambda request, p: None, order=10)
    registry_module.register_person_badges(
        lambda request, p: [{"icon": "cert-other", "tooltip": "x", "severity": None}],
        order=20,
    )
    assert registry_person_badges(object(), person) == [
        {"icon": "cert-other", "tooltip": "x", "severity": None}
    ]


def test_people_list_shows_certificate_badge(client, make_user):
    manager = make_user("manager")
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person,
        name="Forklift licence",
        category=CertificateCategory.FORKLIFT,
        expiry_date=TODAY - timedelta(days=1),
    )
    client.force_login(manager)
    resp = client.get(reverse("people_list"))
    body = resp.content.decode()
    assert "cert-badge-expired" in body
    assert "Preukaz na VZV" in body  # default-Slovak tooltip text
    assert "Forklift licence" not in body


@pytest.mark.parametrize(
    ("language", "expected_name", "expected_expiry"),
    [
        ("sk", "Žeriavnický preukaz", "platnosť do"),
        ("hu", "Darukezelői jogosítvány", "lejár"),
        ("uk", "Посвідчення кранівника", "діє до"),
    ],
)
def test_certificate_badge_translates_canonical_name_and_tooltip(
    client, make_user, language, expected_name, expected_expiry
):
    manager = make_user("manager")
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person,
        name="Crane licence",
        category=CertificateCategory.CRANE,
        expiry_date=date(2027, 6, 20),
    )
    request = client.get(reverse("people_list")).wsgi_request
    request.user = manager

    with translation.override(language):
        tooltip = certificate_badges(request, person)[0]["tooltip"]

    assert expected_name in tooltip
    assert expected_expiry in tooltip
    assert "Crane licence" not in tooltip


def test_person_detail_shows_certificate_badge(client, make_user):
    manager = make_user("manager")
    person = Person.objects.create(first_name="A", last_name="B")
    Certificate.objects.create(
        person=person, name="Health check", category=CertificateCategory.HEALTH
    )
    client.force_login(manager)
    resp = client.get(reverse("person_detail", args=[person.pk]))
    body = resp.content.decode()
    assert "Health check" in body


def test_no_certificate_badges_shown_when_person_has_none(client, make_user):
    manager = make_user("manager")
    Person.objects.create(first_name="A", last_name="B")
    client.force_login(manager)
    resp = client.get(reverse("people_list"))
    assert b"cert-badges" not in resp.content
