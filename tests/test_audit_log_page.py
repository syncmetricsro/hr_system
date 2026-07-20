from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.audit.services import record_event
from core.audit.presentation import audit_action_label
from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def users(django_user_model):
    make = django_user_model.objects.create_user
    return {
        "manager": make(email="au-m@demo.jober.test", password="x", role="manager"),
        "observer": make(email="au-o@demo.jober.test", password="x", role="observer"),
        "coordinator": make(email="au-c@demo.jober.test", password="x", role="coordinator"),
    }


@pytest.fixture
def events(users):
    person = Person.objects.create(first_name="Audit", last_name="Subject")
    record_event(users["manager"], "person.status_changed", target=person, reason="test A")
    record_event(users["observer"], "export.approved", reason="test B")
    return person


def test_managers_and_observers_can_view(client, users, events):
    for role in ("manager", "observer"):
        client.force_login(users[role])
        response = client.get(reverse("audit_log"))
        assert response.status_code == 200, role
        assert b"person.status_changed" in response.content
        assert b'class="data-table-scroll"' in response.content
        assert b'class="data-table audit-table"' in response.content
        assert b'class="audit-when"' in response.content


def test_coordinator_denied(client, users, events):
    client.force_login(users["coordinator"])
    assert client.get(reverse("audit_log")).status_code == 403


def test_filters_by_actor_and_action(client, users, events):
    # The action dropdown always lists every known action, so assertions use
    # the row-only reason strings ("test A"/"test B") to check the table.
    client.force_login(users["manager"])
    resp = client.get(reverse("audit_log"), {"actor": "au-o@"})
    body = resp.content.decode()
    assert "test B" in body and "test A" not in body

    resp = client.get(reverse("audit_log"), {"action": "person.status_changed"})
    body = resp.content.decode()
    assert "test A" in body and "test B" not in body

    resp = client.get(reverse("audit_log"), {"target": "Person"})
    body = resp.content.decode()
    assert "test A" in body and "test B" not in body


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Room assigned"),
        ("sk", "Izba pridelená"),
        ("hu", "Szoba hozzárendelve"),
        ("uk", "Кімнату призначено"),
    ],
)
def test_audit_action_labels_cover_all_ui_languages(language, expected):
    with translation.override(language):
        assert audit_action_label("room.assigned") == expected


@pytest.mark.jober_only
def test_audit_filter_keeps_machine_code_and_displays_translated_label(client, users):
    record_event(users["manager"], "room.assigned")
    client.force_login(users["manager"])
    with translation.override("uk"):
        body = client.get("/uk/audit/").content.decode()

    assert '<option value="room.assigned">Кімнату призначено</option>' in body
    assert "<td>Кімнату призначено</td>" in body

def test_request_errors_reach_console_logging(settings):
    """Production-readiness: 500s must surface in container logs."""
    assert settings.LOGGING["loggers"]["django.request"]["level"] == "ERROR"
    assert settings.LOGGING["loggers"]["django.request"]["handlers"] == ["console"]
    assert settings.LOGGING["root"]["handlers"] == ["console"]
