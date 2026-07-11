from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.messaging"):
    pytest.skip("features.messaging is not installed for this client", allow_module_level=True)


import base64
import hashlib
import hmac

import pytest
from django.urls import reverse

from core.accounts.permissions import Action, can
from features.messaging import services
from features.messaging.models import InboundMessage, OutboundMessage
from core.people.models import Person
from core.projects.models import Project

pytestmark = pytest.mark.django_db

TOKEN = "test-auth-token"


@pytest.fixture
def make_user(django_user_model):
    def _make(role, email=None):
        return django_user_model.objects.create_user(
            email=email or f"{role}@demo.jober.test", password="x", role=role
        )
    return _make


# --- send ---------------------------------------------------------------------

def test_send_sms_records_sent_when_provider_ok(monkeypatch, make_user):
    monkeypatch.setattr(services, "_twilio_send", lambda to, body: "SM123")
    person = Person.objects.create(first_name="A", last_name="B", phone="+421900000000")
    msg = services.send_sms(person.phone, "Hello", actor=make_user("manager"), person=person)
    assert msg.status == OutboundMessage.Status.SENT
    assert msg.provider_sid == "SM123"


def test_send_sms_unconfigured_fails_closed(settings, make_user):
    settings.TWILIO_ACCOUNT_SID = ""
    settings.TWILIO_AUTH_TOKEN = ""
    settings.TWILIO_FROM_NUMBER = ""
    msg = services.send_sms("+421900000000", "Hi", actor=make_user("manager"))
    assert msg.status == OutboundMessage.Status.FAILED
    assert "configured" in msg.error.lower()


# --- signature verification ---------------------------------------------------

def test_signature_accept_and_reject(settings):
    settings.TWILIO_AUTH_TOKEN = TOKEN
    url = "https://jober.example/webhooks/twilio/inbound/"
    params = {"From": "+421900", "Body": "Hi", "MessageSid": "SM1"}
    base = url + "".join(f"{k}{params[k]}" for k in sorted(params))
    good = base64.b64encode(hmac.new(TOKEN.encode(), base.encode(), hashlib.sha1).digest()).decode()
    assert services.verify_twilio_signature(url, params, good) is True
    assert services.verify_twilio_signature(url, params, "wrong") is False


def test_inbound_webhook_rejects_bad_signature(client, settings):
    settings.TWILIO_AUTH_TOKEN = TOKEN
    resp = client.post(reverse("twilio_inbound"), {"From": "+421", "Body": "x"}, HTTP_X_TWILIO_SIGNATURE="bad")
    assert resp.status_code == 403
    assert not InboundMessage.objects.exists()


def test_inbound_webhook_accepts_valid_signature(client, settings):
    settings.TWILIO_AUTH_TOKEN = TOKEN
    url = "http://testserver" + reverse("twilio_inbound")
    params = {"From": "+421900", "Body": "Hello", "MessageSid": "SM9"}
    base = url + "".join(f"{k}{params[k]}" for k in sorted(params))
    sig = base64.b64encode(hmac.new(TOKEN.encode(), base.encode(), hashlib.sha1).digest()).decode()
    resp = client.post(reverse("twilio_inbound"), params, HTTP_X_TWILIO_SIGNATURE=sig)
    assert resp.status_code == 200
    assert InboundMessage.objects.filter(from_number="+421900").exists()


# --- RBAC + coordinator scope -------------------------------------------------

def test_sms_send_rbac(make_user):
    assert can(make_user("recruiter"), Action.SMS_SEND)
    assert can(make_user("coordinator"), Action.SMS_SEND)
    assert not can(make_user("observer"), Action.SMS_SEND)


def test_send_view_denied_for_observer(client, make_user):
    person = Person.objects.create(first_name="A", last_name="B", phone="+421900000000")
    client.force_login(make_user("observer"))
    assert client.post(reverse("send_sms", args=[person.pk]), {"body": "hi"}).status_code == 403


def test_coordinator_cannot_message_outside_their_projects(client, make_user, monkeypatch):
    monkeypatch.setattr(services, "_twilio_send", lambda to, body: "SM1")
    coord = make_user("coordinator")
    person = Person.objects.create(first_name="A", last_name="B", phone="+421900000000")  # no project link
    client.force_login(coord)
    assert client.post(reverse("send_sms", args=[person.pk]), {"body": "hi"}).status_code == 403


def test_coordinator_can_message_own_project_person(client, make_user, monkeypatch):
    monkeypatch.setattr(services, "_twilio_send", lambda to, body: "SM1")
    coord = make_user("coordinator")
    project = Project.objects.create(name="DHL", code="DHLBA")
    project.responsible_coordinators.add(coord)
    person = Person.objects.create(first_name="A", last_name="B", phone="+421900000000")
    from core.projects.services import activate_on_project
    activate_on_project(person, project, actor=coord)
    client.force_login(coord)
    resp = client.post(reverse("send_sms", args=[person.pk]), {"body": "hi"})
    assert resp.status_code == 302  # redirect back to person_detail after sending
    assert OutboundMessage.objects.filter(person=person, status=OutboundMessage.Status.SENT).exists()
