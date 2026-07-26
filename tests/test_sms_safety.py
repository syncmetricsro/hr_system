"""SMS must not be able to reach a real number from a non-production app.

Staging carries live Twilio credentials and fictional worker data. Those two
facts together are the risk: a fictional person record with a real phone number
typed into it is indistinguishable from any other, so "the data is fake" is not
a control. `SMS_ALLOWED_RECIPIENTS` is.

The second concern here is honesty rather than safety. With Twilio unset,
`send_sms` recorded the message as FAILED — so "just remove the credentials"
made the feature look broken instead of unavailable, which is why the demo
runbook resorted to telling the presenter not to press the button.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.messaging"):
    pytest.skip("Messaging feature not installed", allow_module_level=True)

from features.messaging.models import OutboundMessage  # noqa: E402
from features.messaging.services import send_sms, sms_configured  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

ALLOWED = "+421900000000"
REAL_PERSONS_NUMBER = "+421911222333"


@pytest.fixture
def twilio_configured(settings):
    settings.TWILIO_ACCOUNT_SID = "AC-test"
    settings.TWILIO_AUTH_TOKEN = "token"
    settings.TWILIO_FROM_NUMBER = "+10000000000"
    return settings


def test_allowlist_blocks_an_unlisted_recipient(twilio_configured, monkeypatch):
    twilio_configured.SMS_ALLOWED_RECIPIENTS = [ALLOWED]

    def explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("the provider was called for a blocked recipient")

    monkeypatch.setattr("features.messaging.services._twilio_send", explode)

    message = send_sms(REAL_PERSONS_NUMBER, "hello")

    assert message.status == OutboundMessage.Status.BLOCKED
    assert message.provider_sid == ""


def test_blocked_is_not_recorded_as_a_provider_failure(twilio_configured, monkeypatch):
    """FAILED means Twilio saw it and refused. BLOCKED means we never asked.
    Collapsing the two would make a safety net look like an outage."""
    twilio_configured.SMS_ALLOWED_RECIPIENTS = [ALLOWED]
    monkeypatch.setattr(
        "features.messaging.services._twilio_send", lambda *a, **k: "SM-x"
    )
    message = send_sms(REAL_PERSONS_NUMBER, "hello")
    assert message.status != OutboundMessage.Status.FAILED


def test_allowlisted_recipient_still_sends(twilio_configured, monkeypatch):
    twilio_configured.SMS_ALLOWED_RECIPIENTS = [ALLOWED]
    monkeypatch.setattr(
        "features.messaging.services._twilio_send", lambda *a, **k: "SM-ok"
    )
    message = send_sms(ALLOWED, "hello")
    assert message.status == OutboundMessage.Status.SENT
    assert message.provider_sid == "SM-ok"


def test_allowlist_matches_regardless_of_formatting(twilio_configured, monkeypatch):
    """An allowlist that only matched one spelling of a number would be a trap:
    the entry looks right, the send is blocked, and the reason is invisible."""
    twilio_configured.SMS_ALLOWED_RECIPIENTS = ["+421 900 000 000"]
    monkeypatch.setattr(
        "features.messaging.services._twilio_send", lambda *a, **k: "SM-ok"
    )
    message = send_sms("+421-900-000-000", "hello")
    assert message.status == OutboundMessage.Status.SENT


def test_empty_allowlist_is_unrestricted(twilio_configured, monkeypatch):
    """Production's setting. An empty list must not mean "block everything" -
    that would take messaging down the moment the variable is unset."""
    twilio_configured.SMS_ALLOWED_RECIPIENTS = []
    monkeypatch.setattr(
        "features.messaging.services._twilio_send", lambda *a, **k: "SM-ok"
    )
    message = send_sms(REAL_PERSONS_NUMBER, "hello")
    assert message.status == OutboundMessage.Status.SENT


# --- honest disabled state -------------------------------------------------


def test_sms_configured_is_false_without_credentials(settings):
    settings.TWILIO_ACCOUNT_SID = ""
    settings.TWILIO_AUTH_TOKEN = ""
    settings.TWILIO_FROM_NUMBER = ""
    assert sms_configured() is False


def test_sms_configured_is_true_with_all_three(twilio_configured):
    assert sms_configured() is True


def test_partial_credentials_count_as_unconfigured(twilio_configured):
    """A half-configured app must report unavailable rather than offer a
    button that fails at the provider."""
    twilio_configured.TWILIO_FROM_NUMBER = ""
    assert sms_configured() is False
