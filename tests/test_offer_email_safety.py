"""An offer email must not reach an inbox that did not agree to hear from us.

Two separate risks share this file because they share one code path.

The first is the environment risk `SMS_ALLOWED_RECIPIENTS` already answers for
SMS: staging holds fictional worker records, but a fictional record with a real
address typed into it is indistinguishable from any other, so "the data is
fake" is not a control. `EMAIL_ALLOWED_RECIPIENTS` is.

The second is new here and has no SMS equivalent. `send_sms` consults neither
the opt-out flag nor the blacklist — an operational text to a worker on shift
is a different act from marketing a job to someone who asked us to stop, or to
someone the company blocked. Those checks must run *before* the allowlist and
before the mail server, so a blocked send is never an outbound connection.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.core import mail

if not django_apps.is_installed("features.messaging"):
    pytest.skip("Messaging feature not installed", allow_module_level=True)

from core.people.models import LifecycleStatus, Person  # noqa: E402
from features.messaging.models import (  # noqa: E402
    JobOffer,
    OfferEmailKind,
    OfferEmailTemplate,
    OutboundEmail,
)
from features.messaging.services import send_offer_email  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

ALLOWED = "demo@demo.jober.test"
A_REAL_LOOKING_ADDRESS = "someone@example.com"


@pytest.fixture(autouse=True)
def _locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    mail.outbox.clear()
    return settings


@pytest.fixture
def template():
    return OfferEmailTemplate.objects.create(
        kind=OfferEmailKind.NEW_OFFER,
        language="sk",
        subject="Ponuka: $offer_title",
        body="Dobrý deň, $first_name.",
    )


@pytest.fixture
def offer():
    return JobOffer.objects.create(title="Operátor výroby")


@pytest.fixture
def person():
    return Person.objects.create(
        first_name="Oksana",
        last_name="Kovalenko",
        email=A_REAL_LOOKING_ADDRESS,
        preferred_language="sk",
    )


def _send(offer, person):
    return send_offer_email(offer, person, OfferEmailKind.NEW_OFFER)


# --- the worker's own state ------------------------------------------------


def test_opt_out_blocks_the_send(template, offer, person):
    person.email_opt_out = True
    person.save(update_fields=["email_opt_out"])

    record = _send(offer, person)

    assert record.status == OutboundEmail.Status.BLOCKED
    assert mail.outbox == []


def test_blacklisted_person_is_never_emailed_an_offer(template, offer, person):
    """The SMS path checks neither flag. An offer is exactly the message that
    must not go to someone the company has blocked."""
    person.lifecycle_status = LifecycleStatus.BLACKLISTED
    person.save(update_fields=["lifecycle_status"])

    record = _send(offer, person)

    assert record.status == OutboundEmail.Status.BLOCKED
    assert mail.outbox == []


def test_missing_address_is_blocked_not_failed(template, offer, person):
    person.email = ""
    person.save(update_fields=["email"])

    record = _send(offer, person)

    assert record.status == OutboundEmail.Status.BLOCKED
    assert mail.outbox == []


def test_blocked_send_never_touches_the_mail_server(
    template, offer, person, monkeypatch
):
    def explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("the mail server was called for a blocked recipient")

    monkeypatch.setattr("django.core.mail.EmailMessage.send", explode)
    person.email_opt_out = True
    person.save(update_fields=["email_opt_out"])

    assert _send(offer, person).status == OutboundEmail.Status.BLOCKED


# --- the environment allowlist ---------------------------------------------


def test_allowlist_blocks_an_unlisted_address(settings, template, offer, person):
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]

    record = _send(offer, person)

    assert record.status == OutboundEmail.Status.BLOCKED
    assert mail.outbox == []


def test_blocked_is_not_recorded_as_a_delivery_failure(
    settings, template, offer, person
):
    """FAILED means the mail server saw it and refused; BLOCKED means we never
    asked. Collapsing the two makes a safety net look like an outage."""
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]
    assert _send(offer, person).status != OutboundEmail.Status.FAILED


def test_allowlisted_address_still_sends(settings, template, offer, person):
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]
    person.email = ALLOWED
    person.save(update_fields=["email"])

    record = _send(offer, person)

    assert record.status == OutboundEmail.Status.SENT
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [ALLOWED]


def test_allowlist_ignores_case(settings, template, offer, person):
    """An allowlist that only matched one spelling would be a trap: the entry
    looks right, the send is blocked, and the reason is invisible."""
    settings.EMAIL_ALLOWED_RECIPIENTS = ["Demo@Demo.Jober.Test"]
    person.email = ALLOWED
    person.save(update_fields=["email"])

    assert _send(offer, person).status == OutboundEmail.Status.SENT


def test_empty_allowlist_is_unrestricted(settings, template, offer, person):
    """Production's setting. An empty list must not mean "block everything" —
    that would take the feature down the moment the variable is unset."""
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    assert _send(offer, person).status == OutboundEmail.Status.SENT


# --- honest disabled state -------------------------------------------------
#
# The generic behaviour of `email_configured` and the `mail.W001` deploy check
# moved to tests/test_core_mail.py when the allowlist became a platform control.
# What stays here is what is specific to this transport: that an unconfigured
# backend produces a FAILED record rather than a silent no-op.


def test_unconfigured_smtp_records_failed_and_sends_nothing(
    settings, template, offer, person
):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = ""

    record = _send(offer, person)

    assert record.status == OutboundEmail.Status.FAILED
    assert mail.outbox == []
