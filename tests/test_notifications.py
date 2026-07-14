from __future__ import annotations

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext

from core.audit.services import record_event
from core.notifications.models import NotificationDismissal
from core.notifications.services import SESSION_BASELINE_KEY
from core.people.models import Person
from core.projects.models import PillarState, Project, ReadinessRecord, TrialAssignment

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def staff(django_user_model):
    make = django_user_model.objects.create_user
    return {
        "manager": make(email="notify-manager@demo.jober.test", password="x", role="manager"),
        "other_manager": make(email="notify-other@demo.jober.test", password="x", role="manager"),
        "coordinator": make(email="notify-coord@demo.jober.test", password="x", role="coordinator"),
        "recruiter": make(email="notify-recruiter@demo.jober.test", password="x", role="recruiter"),
        "observer": make(email="notify-observer@demo.jober.test", password="x", role="observer"),
    }


def test_successful_login_sets_session_audit_baseline(client, staff):
    response = client.post(reverse("login"), {"email": staff["manager"].email, "password": "x"})
    assert response.status_code == 302
    assert client.session[SESSION_BASELINE_KEY] == staff["manager"].audit_events.get(action="auth.login").pk


def test_routine_feed_is_session_scoped_and_excludes_own_actions(client, staff):
    person = Person.objects.create(first_name="Activity", last_name="Subject")
    client.force_login(staff["manager"])
    client.get(reverse("notification_panel"))  # establishes baseline for force_login

    record_event(staff["manager"], "person.updated", target=person)
    other_event = record_event(
        staff["other_manager"],
        "person.updated",
        target=person,
        reason="private audit reason must stay out of notifications",
    )

    response = client.get(reverse("notification_panel"))
    updates = response.context["notification_center"]["updates"]
    assert [item.key for item in updates] == [f"audit:{other_event.pk}"]
    assert staff["other_manager"].email in updates[0].detail
    assert other_event.reason not in response.content.decode()


def test_dismissal_is_per_user_and_changed_alert_reappears(client, staff):
    project = Project.objects.create(name="Alert Project", code="ALERT")
    person = Person.objects.create(first_name="Ready", last_name="Later")
    readiness = ReadinessRecord.objects.create(person=person, project=project)
    client.force_login(staff["manager"])

    first = client.get(reverse("notification_panel")).context["notification_center"]
    alert = next(item for item in first["alerts"] if item.key == f"readiness:{readiness.pk}")
    response = client.post(
        reverse("notification_dismiss"),
        {"key": alert.key, "version": alert.version, "next": reverse("reports")},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert NotificationDismissal.objects.filter(user=staff["manager"], item_key=alert.key).exists()
    assert alert.key not in response.content.decode()

    readiness.gear_state = PillarState.COMPLETE
    readiness.save(update_fields=["gear_state", "updated_at"])
    changed = client.get(reverse("notification_panel")).context["notification_center"]
    replacement = next(item for item in changed["alerts"] if item.key == alert.key)
    assert replacement.version != alert.version


def test_forged_dismissal_is_rejected(client, staff):
    client.force_login(staff["manager"])
    response = client.post(
        reverse("notification_dismiss"),
        {"key": "blacklist:forged", "version": "made-up"},
    )
    assert response.status_code == 400
    assert not NotificationDismissal.objects.exists()


def test_coordinator_sees_only_own_project_alerts_and_recruiter_cannot_resolve(client, staff):
    own = Project.objects.create(name="Own", code="OWN")
    other = Project.objects.create(name="Other", code="OTHER")
    own.responsible_coordinators.add(staff["coordinator"])
    own_person = Person.objects.create(first_name="Own", last_name="Worker", owning_recruiter=staff["recruiter"])
    other_person = Person.objects.create(first_name="Other", last_name="Worker")
    own_trial = TrialAssignment.objects.create(person=own_person, project=own)
    TrialAssignment.objects.create(person=other_person, project=other)

    client.force_login(staff["coordinator"])
    coordinator_alerts = client.get(reverse("notification_panel")).context["notification_center"]["alerts"]
    assert [item.key for item in coordinator_alerts if item.key.startswith("trial-outcome:")] == [
        f"trial-outcome:{own_trial.pk}"
    ]

    client.force_login(staff["recruiter"])
    recruiter_alerts = client.get(reverse("notification_panel")).context["notification_center"]["alerts"]
    assert not any(item.key.startswith("trial-outcome:") for item in recruiter_alerts)


def test_observer_has_no_operational_notification_center(client, staff):
    client.force_login(staff["observer"])
    response = client.get(reverse("reports"))
    assert response.status_code == 200
    assert b'id="notification-center"' not in response.content


def test_htmx_unsafe_response_triggers_notification_refresh(client, staff):
    project = Project.objects.create(name="Trigger", code="TRIGGER")
    person = Person.objects.create(first_name="Trigger", last_name="Worker")
    client.force_login(staff["manager"])
    response = client.post(
        reverse("assign_trial", args=[person.pk]),
        {"project": project.pk, "scheduled_for": "2026-07-14T09:30"},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 302
    assert "notificationsChanged" in response["HX-Trigger"]


def test_dismiss_requires_csrf(staff):
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(staff["manager"])
    response = csrf_client.post(
        reverse("notification_dismiss"),
        {"key": "anything", "version": "anything"},
    )
    assert response.status_code == 403


def test_feature_alert_destinations_and_resolved_state_disappearance(client, staff, settings):
    from features.blacklist.models import BlacklistCase, BlacklistCaseStatus
    from features.checklists.models import (
        ChecklistItemTemplate,
        ChecklistTemplate,
        PersonChecklistItem,
    )
    from features.feedback.models import FeedbackLink, FeedbackSubmission
    from features.logistics.models import (
        DeductionReviewStatus,
        EquipmentIssue,
        EquipmentItem,
    )

    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "checklists": True}
    person = Person.objects.create(
        first_name="Feature",
        last_name="Alerts",
        lifecycle_status="working",
    )
    item = EquipmentItem.objects.create(name="Boots", unit_price="45.00")
    issue = EquipmentIssue.objects.create(
        person=person,
        item=item,
        review_status=DeductionReviewStatus.PENDING,
        charge_amount="45.00",
    )
    case = BlacklistCase.objects.create(person=person)
    feedback_link = FeedbackLink.objects.create(label="Workshop")
    FeedbackSubmission.objects.create(link=feedback_link, message="Fictional feedback")
    checklist = ChecklistTemplate.objects.create(name="Activation")
    checklist_template_item = ChecklistItemTemplate.objects.create(
        template=checklist,
        label="Contract signed",
        critical=True,
    )
    checklist_item = PersonChecklistItem.objects.create(
        person=person,
        item_template=checklist_template_item,
    )

    client.force_login(staff["manager"])
    alerts = client.get(reverse("notification_panel")).context["notification_center"]["alerts"]
    by_key = {alert.key: alert for alert in alerts}
    assert by_key["compliance:open"].url == reverse("compliance_list")
    assert by_key["equipment:pending-reviews"].url == reverse("equipment_reviews")
    assert by_key["blacklist:proposed"].url == reverse("blacklist_queue")
    assert by_key["feedback:inbox"].url == reverse("feedback_inbox")
    assert by_key[f"checklist:{person.pk}"].url == reverse("person_detail", args=[person.pk])

    person.lifecycle_status = "available"
    person.save(update_fields=["lifecycle_status", "updated_at", "search_name"])
    issue.review_status = DeductionReviewStatus.WAIVED
    issue.save(update_fields=["review_status"])
    case.status = BlacklistCaseStatus.REJECTED
    case.save(update_fields=["status", "updated_at"])
    checklist_item.done = True
    checklist_item.save(update_fields=["done"])

    resolved = client.get(reverse("notification_panel")).context["notification_center"]["alerts"]
    resolved_keys = {alert.key for alert in resolved}
    assert "compliance:open" not in resolved_keys
    assert "equipment:pending-reviews" not in resolved_keys
    assert "blacklist:proposed" not in resolved_keys
    assert f"checklist:{person.pk}" not in resolved_keys
    assert "feedback:inbox" in resolved_keys


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Notifications"),
        ("sk", "Upozornenia"),
        ("hu", "Értesítések"),
        ("uk", "Сповіщення"),
    ],
)
def test_notification_center_is_translated_in_all_ui_languages(language, expected):
    with translation.override(language):
        assert gettext("Notifications") == expected
