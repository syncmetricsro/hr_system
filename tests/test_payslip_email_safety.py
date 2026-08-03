"""A payslip must not reach an inbox this environment was not told to allow.

CorvinumEU's demo points at a live mail server (`noreply@corvinum.eu`), and
until this guard existed `send_payslip` mailed `payslip.sent_to or
person.email` unconditionally. The only protection was procedure: a runbook
telling the presenter to use a controlled test mailbox. That is precisely the
control `tests/test_sms_safety.py` rejects — a fictional person record with a
real address typed into it is indistinguishable from any other, so "the data is
fake" is not a control.

Deliberately **not** `jober_only`: `features.payslips` is installed for both
clients, and the corvinum lane is the one that matters here. Jober merely has
the flag off.

The second concern is ordering. The one-time password exists only in the
caller's flash message, so it must not be minted for a send that is about to be
refused — otherwise a presenter reads out a password for an email nobody got.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.conf import settings as django_settings
from django.core import mail
from django.urls import reverse

from core.audit.models import AuditEvent
from core.people.models import Person
from features.payslips.models import Payslip
from features.payslips.services import PayslipError, send_payslip

pytestmark = pytest.mark.django_db

# Same gate tests/test_payslips.py uses: the service is importable for both
# clients, but the URL only exists where the flag is on.
payslip_ui = pytest.mark.skipif(
    not django_settings.FEATURE_FLAGS.get("payslips", False),
    reason="Payslip UI is not mounted for this client",
)

ALLOWED = "demo@demo.corvinum.test"
A_REAL_LOOKING_ADDRESS = "someone@example.com"


@pytest.fixture(autouse=True)
def _locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    mail.outbox.clear()
    return settings


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="ps-safety-manager@demo.jober.test", password="x", role="manager"
    )


@pytest.fixture
def payslip():
    person = Person.objects.create(
        first_name="Eszter", last_name="Varga", email=A_REAL_LOOKING_ADDRESS
    )
    return Payslip.objects.create(
        person=person, period="2026-07", net_amount=Decimal("850.00")
    )


# --- the allowlist ---------------------------------------------------------


def test_unlisted_recipient_is_refused(settings, payslip, manager):
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]

    with pytest.raises(PayslipError):
        send_payslip(payslip, actor=manager)

    assert mail.outbox == []


def test_a_refused_send_is_not_recorded_as_delivered(settings, payslip, manager):
    """`sent_at` is what the UI shows as proof of delivery. A blocked attempt
    that set it would be worse than no guard at all."""
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]

    with pytest.raises(PayslipError):
        send_payslip(payslip, actor=manager)

    payslip.refresh_from_db()
    assert payslip.sent_at is None
    assert payslip.sent_to == ""


def test_no_password_or_pdf_is_generated_for_a_refused_send(
    settings, payslip, manager, monkeypatch
):
    """The guard runs before the password and the PDF, not merely before the
    send. A minted password with no email behind it is a password a presenter
    reads out for nothing."""
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]

    def explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("a PDF was built for a blocked recipient")

    monkeypatch.setattr("features.payslips.services.build_encrypted_pdf", explode)

    with pytest.raises(PayslipError):
        send_payslip(payslip, actor=manager)


def test_a_refused_send_is_audited(settings, payslip, manager):
    """Only successes were audited before. A refused send is evidence."""
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]

    with pytest.raises(PayslipError):
        send_payslip(payslip, actor=manager)

    event = AuditEvent.objects.get(action="payslip.send_blocked")
    assert event.actor == manager
    assert not AuditEvent.objects.filter(action="payslip.sent").exists()


def test_listed_recipient_still_sends(settings, payslip, manager):
    """The guard refuses the *other* address, not everything."""
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]
    payslip.person.email = ALLOWED
    payslip.person.save(update_fields=["email"])

    password = send_payslip(payslip, actor=manager)

    assert password
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [ALLOWED]
    payslip.refresh_from_db()
    assert payslip.sent_at is not None


def test_empty_allowlist_is_unrestricted(settings, payslip, manager):
    """Production's setting — an unset variable must not break payslips."""
    settings.EMAIL_ALLOWED_RECIPIENTS = []

    send_payslip(payslip, actor=manager)

    assert len(mail.outbox) == 1


def test_matching_ignores_case(settings, payslip, manager):
    settings.EMAIL_ALLOWED_RECIPIENTS = ["Demo@Demo.Corvinum.Test"]
    payslip.person.email = ALLOWED
    payslip.person.save(update_fields=["email"])

    send_payslip(payslip, actor=manager)

    assert len(mail.outbox) == 1


# --- the resend path -------------------------------------------------------


def test_resend_rechecks_the_recorded_address(settings, payslip, manager):
    """`send_payslip` prefers `sent_to` over `person.email`, so a payslip
    delivered before this guard existed carries an address that was never
    checked. A resend must not inherit that."""
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    send_payslip(payslip, actor=manager)  # records sent_to = the real address
    mail.outbox.clear()

    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]
    # Even correcting the person's address must not help: the resend uses
    # sent_to, which is exactly why the guard reads the resolved value.
    payslip.person.email = ALLOWED
    payslip.person.save(update_fields=["email"])

    with pytest.raises(PayslipError):
        send_payslip(payslip, actor=manager)

    assert mail.outbox == []


# --- through the view ------------------------------------------------------


@payslip_ui
def test_view_reports_the_refusal_instead_of_erroring(
    client, settings, payslip, manager
):
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]
    client.force_login(manager)

    response = client.post(reverse("payslip_send", args=[payslip.pk]))

    assert response.status_code == 302
    assert mail.outbox == []
    payslip.refresh_from_db()
    assert payslip.sent_at is None
