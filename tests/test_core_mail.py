"""The recipient allowlist is a platform control, not a messaging one.

It began inside `features.messaging` (ADR 0029) and had to move: CorvinumEU
installs `features.payslips` and *not* `features.messaging`, so a guard living
in the messaging feature protected the one client that never needed it and left
the one about to be pointed at a live mail server unguarded. The same applied to
the deploy check, which was gated on `FEATURE_FLAGS["offer_emails"]` — always
False on CorvinumEU.

No `jober_only` marker and no module skip: core is installed everywhere, and
running in both lanes is the whole point of the move.
"""

from __future__ import annotations

import pytest

from core.checks import worker_email_allowlist_check
from core.mail import (
    EmailRecipientNotAllowed,
    allowed_recipients,
    assert_recipient_allowed,
    email_configured,
    recipient_allowed,
)

ALLOWED = "demo@demo.jober.test"
A_REAL_LOOKING_ADDRESS = "someone@example.com"


# --- allowlist semantics ---------------------------------------------------


def test_empty_allowlist_is_unrestricted(settings):
    """Production's setting. An empty list must not mean "block everything" —
    that would take every email path down the moment the variable is unset."""
    settings.EMAIL_ALLOWED_RECIPIENTS = []

    assert recipient_allowed(A_REAL_LOOKING_ADDRESS) is True
    assert_recipient_allowed(A_REAL_LOOKING_ADDRESS)  # does not raise


def test_unlisted_address_is_refused(settings):
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]

    assert recipient_allowed(A_REAL_LOOKING_ADDRESS) is False
    with pytest.raises(EmailRecipientNotAllowed):
        assert_recipient_allowed(A_REAL_LOOKING_ADDRESS)


def test_listed_address_is_allowed(settings):
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]
    assert recipient_allowed(ALLOWED) is True


def test_matching_ignores_case_and_whitespace(settings):
    """An allowlist that only matched one spelling would be a trap: the entry
    looks right, the send is refused, and the reason is invisible."""
    settings.EMAIL_ALLOWED_RECIPIENTS = ["  Demo@Demo.Jober.Test  "]
    assert recipient_allowed(" demo@demo.jober.test ") is True


def test_blank_address_is_refused_when_a_list_exists(settings):
    settings.EMAIL_ALLOWED_RECIPIENTS = [ALLOWED]
    assert recipient_allowed("") is False


def test_unset_setting_behaves_as_unrestricted(settings):
    delattr(settings, "EMAIL_ALLOWED_RECIPIENTS")
    assert allowed_recipients() == []
    assert recipient_allowed(A_REAL_LOOKING_ADDRESS) is True


# --- configured state ------------------------------------------------------


def test_console_backend_counts_as_configured(settings):
    """Otherwise every local demo and every test renders its send control as
    unavailable."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    assert email_configured() is True


def test_locmem_backend_counts_as_configured(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    assert email_configured() is True


def test_an_empty_backend_is_unconfigured(settings):
    """Not a harmless no-op backend: Django cannot import "" so every send
    raises ImportError. Jober staging had exactly this — `DJANGO_EMAIL_BACKEND`
    set to an empty string beside live SMTP credentials — which made the UI
    offer a Send button that could only ever error."""
    settings.EMAIL_BACKEND = ""
    assert email_configured() is False


def test_a_whitespace_backend_is_unconfigured(settings):
    settings.EMAIL_BACKEND = "   "
    assert email_configured() is False


def test_smtp_without_a_host_is_unconfigured(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = ""
    assert email_configured() is False


def test_smtp_with_a_host_is_configured(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "smtp.example.test"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.test"
    assert email_configured() is True


# --- the deploy check ------------------------------------------------------


def _smtp(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "smtp.example.test"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.test"
    settings.DEBUG = False


def test_check_warns_for_offer_emails(settings):
    _smtp(settings)
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "offer_emails": True}
    settings.EMAIL_ALLOWED_RECIPIENTS = []

    assert [w.id for w in worker_email_allowlist_check(None)] == ["mail.W001"]


def test_check_warns_for_payslips_too(settings):
    """The bug this move fixes. The old check was gated on `offer_emails`,
    which is False on CorvinumEU — the client that actually has a live mail
    server pointed at it."""
    _smtp(settings)
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        "offer_emails": False,
        "payslips": True,
    }
    settings.EMAIL_ALLOWED_RECIPIENTS = []

    assert [w.id for w in worker_email_allowlist_check(None)] == ["mail.W001"]


def test_check_is_quiet_with_an_allowlist(settings):
    _smtp(settings)
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "payslips": True}
    settings.EMAIL_ALLOWED_RECIPIENTS = ["demo@demo.corvinum.test"]

    assert worker_email_allowlist_check(None) == []


def test_check_is_quiet_when_no_feature_sends_worker_email(settings):
    _smtp(settings)
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        "offer_emails": False,
        "payslips": False,
    }
    settings.EMAIL_ALLOWED_RECIPIENTS = []

    assert worker_email_allowlist_check(None) == []


def test_check_is_quiet_on_a_console_backend(settings):
    """A local demo cannot leak anywhere, so warning there is noise that
    teaches people to ignore the warning that matters."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    settings.DEBUG = False
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "payslips": True}
    settings.EMAIL_ALLOWED_RECIPIENTS = []

    assert worker_email_allowlist_check(None) == []


def test_check_is_quiet_under_debug(settings):
    _smtp(settings)
    settings.DEBUG = True
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "payslips": True}
    settings.EMAIL_ALLOWED_RECIPIENTS = []

    assert worker_email_allowlist_check(None) == []
