from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser

from core.audit.models import AuditError, AuditEvent
from core.audit.services import record_event

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        email="aktor@demo.jober.test", password="x", role="manager"
    )


def test_record_event_creates_row(user):
    event = record_event(user, "test.action", reason="lebo", note="hi")
    assert event.pk is not None
    assert event.actor == user
    assert event.action == "test.action"
    assert event.reason == "lebo"
    assert event.metadata == {"note": "hi"}


def test_record_event_with_target(user):
    event = record_event(user, "test.target", target=user)
    assert event.target_type == "User"
    assert event.target_id == str(user.pk)


def test_record_event_anonymous_actor_is_none():
    event = record_event(AnonymousUser(), "system.event")
    assert event.actor is None


def test_audit_event_is_immutable(user):
    event = record_event(user, "test.action")
    event.reason = "zmena"
    with pytest.raises(AuditError):
        event.save()


def test_audit_event_cannot_be_deleted(user):
    event = record_event(user, "test.action")
    with pytest.raises(AuditError):
        event.delete()
    assert AuditEvent.objects.filter(pk=event.pk).exists()
