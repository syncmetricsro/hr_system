from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.accounts.permissions import Action, can
from core.audit.services import record_event
from core.audit.presentation import audit_action_label, audit_reason_label
from core.people.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def users(django_user_model):
    make = django_user_model.objects.create_user
    return {
        "manager": make(email="au-m@demo.jober.test", password="x", role="manager"),
        "observer": make(email="au-o@demo.jober.test", password="x", role="observer"),
        "coordinator": make(
            email="au-c@demo.jober.test", password="x", role="coordinator"
        ),
    }


@pytest.fixture
def events(users):
    person = Person.objects.create(first_name="Audit", last_name="Subject")
    record_event(
        users["manager"], "person.status_changed", target=person, reason="test A"
    )
    record_event(users["observer"], "export.approved", reason="test B")
    return person


def test_exactly_the_roles_the_policy_allows_can_view(client, users, events):
    """Asserted against the running client's policy rather than a fixed role
    list. CorvinumEU narrowed audit to the Observer on 2026-08-04 while Jober
    keeps it for managers, and a hard-coded role would only ever test one of
    them — this way each client tests its own answer, and that the answer is
    actually enforced."""
    for role, user in users.items():
        client.force_login(user)
        response = client.get(reverse("audit_log"))
        allowed = can(user, Action.AUDIT_VIEW)
        assert response.status_code == (200 if allowed else 403), role
        if not allowed:
            continue
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
    client.force_login(users["observer"])
    resp = client.get(reverse("audit_log"), {"actor": "au-o@"})
    body = resp.content.decode()
    assert "test B" in body and "test A" not in body

    resp = client.get(reverse("audit_log"), {"action": "person.status_changed"})
    body = resp.content.decode()
    assert "test A" in body and "test B" not in body

    resp = client.get(reverse("audit_log"), {"target": "Person"})
    body = resp.content.decode()
    assert "test A" in body and "test B" not in body


def test_filters_by_target_worker(client, users, events):
    other_person = Person.objects.create(first_name="Other", last_name="Worker")
    record_event(
        users["coordinator"],
        "person.status_changed",
        target=other_person,
        reason="test C",
    )

    client.force_login(users["observer"])

    resp = client.get(reverse("audit_log"), {"worker": "audit subject"})
    body = resp.content.decode()
    assert "test A" in body and "test C" not in body

    resp = client.get(reverse("audit_log"), {"worker": "other"})
    body = resp.content.decode()
    assert "test C" in body and "test A" not in body


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


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Activated onto a project"),
        ("sk", "Aktivovaný na projekte"),
        ("hu", "Aktiválva a projektre"),
        ("uk", "Активовано на проєкті"),
    ],
)
def test_audit_reason_labels_cover_all_ui_languages(language, expected):
    with translation.override(language):
        assert audit_reason_label("activation") == expected


def test_audit_reason_label_passes_through_unknown_free_text_unchanged():
    with translation.override("uk"):
        assert audit_reason_label("Called in sick, replaced by another worker") == (
            "Called in sick, replaced by another worker"
        )


@pytest.mark.jober_only
def test_audit_log_page_translates_known_reason_but_not_free_text(client, users):
    person = Person.objects.create(first_name="Reason", last_name="Test")
    record_event(
        users["manager"], "assignment.created", target=person, reason="activation"
    )
    record_event(
        users["manager"], "person.updated", target=person, reason="Called in sick today"
    )
    client.force_login(users["manager"])

    with translation.override("uk"):
        body = client.get("/uk/audit/").content.decode()

    assert "Активовано на проєкті" in body
    assert "Called in sick today" in body
    # The raw reason code must not be rendered *as content*. Scoped to the
    # table cell rather than the whole page: audit_log.html renders reasons in
    # <td class="muted">, and a bare page-wide substring check also matched
    # unrelated nav URLs (/uk/activations/) once an activation queue existed.
    assert ">activation<" not in body
    assert '<td class="muted">activation</td>' not in body


def test_request_errors_reach_console_logging(settings):
    """Production-readiness: 500s must surface in container logs."""
    assert settings.LOGGING["loggers"]["django.request"]["level"] == "ERROR"
    assert settings.LOGGING["loggers"]["django.request"]["handlers"] == ["console"]
    assert settings.LOGGING["root"]["handlers"] == ["console"]
