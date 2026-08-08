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

from core.checks import smtp_transport_security_check, worker_email_allowlist_check
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


def test_the_default_localhost_host_is_unconfigured(settings):
    """`localhost` is base.py's os.getenv fallback, not a chosen mail server.
    Reading it as configured made `scripts/dev_app.sh` present an enabled Send
    button on a Jober demo with no SMTP at all, so every press filed a FAILED
    record against a refused connection on port 587."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "localhost"
    settings.DEFAULT_FROM_EMAIL = "noreply@localhost"
    assert email_configured() is False


def test_an_explicit_local_mta_is_configured(settings):
    """Someone genuinely relaying through a local MTA names it explicitly, so
    the rule above must not lock them out."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "127.0.0.1"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.test"
    assert email_configured() is True


def test_smtp_with_a_host_is_configured(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "smtp.example.test"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.test"
    assert email_configured() is True


def test_implicit_ssl_smtp_is_configured(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "smtp.example.test"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.test"
    settings.EMAIL_USE_TLS = False
    settings.EMAIL_USE_SSL = True

    assert email_configured() is True


def test_smtp_with_tls_and_ssl_is_unconfigured(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "smtp.example.test"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.test"
    settings.EMAIL_USE_TLS = True
    settings.EMAIL_USE_SSL = True

    assert email_configured() is False


# --- the deploy check ------------------------------------------------------


def _smtp(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = "smtp.example.test"
    settings.DEFAULT_FROM_EMAIL = "noreply@example.test"
    settings.DEBUG = False


def test_check_rejects_tls_and_ssl_together(settings):
    _smtp(settings)
    settings.EMAIL_USE_TLS = True
    settings.EMAIL_USE_SSL = True

    errors = smtp_transport_security_check(None)

    assert [error.id for error in errors] == ["mail.E001"]


def test_transport_check_accepts_implicit_ssl(settings):
    _smtp(settings)
    settings.EMAIL_USE_TLS = False
    settings.EMAIL_USE_SSL = True

    assert smtp_transport_security_check(None) == []


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


# --- domain entries (2026-08-09) -------------------------------------------
#
# Listing every tester's address is the wrong unit for how these environments
# are used: the client's own people enter their own addresses. An entry
# beginning with @ is a whole domain.
#
# Matching is deliberately exact. @jober.sk allows anna@jober.sk and refuses
# anna@mail.jober.sk, because subdomain matching makes the blast radius
# invisible - every present and future subdomain becomes sendable without the
# setting changing.

DOMAIN = "@jober.sk"


def test_a_domain_entry_allows_addresses_at_that_domain(settings):
    settings.EMAIL_ALLOWED_RECIPIENTS = [DOMAIN]

    assert recipient_allowed("anna@jober.sk") is True
    assert recipient_allowed("someone.else@jober.sk") is True


def test_a_domain_entry_refuses_other_domains(settings):
    settings.EMAIL_ALLOWED_RECIPIENTS = [DOMAIN]

    assert recipient_allowed("anna@notjober.sk") is False
    assert recipient_allowed(A_REAL_LOOKING_ADDRESS) is False


def test_a_domain_entry_does_not_cover_subdomains(settings):
    """The decision, asserted, because it is the one a later reader will be
    tempted to 'fix'. A subdomain is listed separately when it is wanted."""
    settings.EMAIL_ALLOWED_RECIPIENTS = [DOMAIN]

    assert recipient_allowed("anna@mail.jober.sk") is False

    settings.EMAIL_ALLOWED_RECIPIENTS = [DOMAIN, "@mail.jober.sk"]
    assert recipient_allowed("anna@mail.jober.sk") is True


def test_domain_and_exact_entries_mix(settings):
    settings.EMAIL_ALLOWED_RECIPIENTS = ["@mozmail.com", ALLOWED]

    assert recipient_allowed("tester@mozmail.com") is True
    assert recipient_allowed(ALLOWED) is True
    assert recipient_allowed(A_REAL_LOOKING_ADDRESS) is False


def test_domain_matching_ignores_case_and_whitespace(settings):
    settings.EMAIL_ALLOWED_RECIPIENTS = ["  @Jober.SK  "]

    assert recipient_allowed(" Anna@JOBER.sk ") is True


def test_a_bare_at_entry_matches_nothing(settings):
    """Read as 'any domain' it would silently unrestrict the environment, which
    is the opposite of what somebody typing into an allowlist intends."""
    settings.EMAIL_ALLOWED_RECIPIENTS = ["@"]

    assert recipient_allowed(A_REAL_LOOKING_ADDRESS) is False
    assert recipient_allowed("anyone@anywhere.test") is False


def test_the_domain_is_taken_from_the_last_at(settings):
    """A quoted local part must not be able to smuggle a domain in."""
    settings.EMAIL_ALLOWED_RECIPIENTS = [DOMAIN]

    assert recipient_allowed('"anna@jober.sk"@evil.test') is False


def test_the_refusal_names_the_address(settings):
    """The likeliest refusal is a subdomain somebody assumed was covered.
    Naming it sends the reader to the setting instead of to the logs."""
    from django.utils import translation

    settings.EMAIL_ALLOWED_RECIPIENTS = [DOMAIN]

    with translation.override("en"):
        with pytest.raises(EmailRecipientNotAllowed) as raised:
            assert_recipient_allowed("anna@mail.jober.sk")

    assert "anna@mail.jober.sk" in str(raised.value)


# --- the deploy check for unusable entries ---------------------------------


def test_an_entry_without_an_at_is_reported(settings):
    """mozmail.com instead of @mozmail.com: read as an address nobody has, so
    every send is refused with nothing on screen explaining it."""
    from core.checks import worker_email_allowlist_syntax_check

    settings.EMAIL_ALLOWED_RECIPIENTS = ["mozmail.com"]

    warnings = worker_email_allowlist_syntax_check(None)

    assert [w.id for w in warnings] == ["mail.W002"]
    assert "mozmail.com" in warnings[0].msg


def test_a_bare_at_entry_is_reported(settings):
    from core.checks import worker_email_allowlist_syntax_check

    settings.EMAIL_ALLOWED_RECIPIENTS = ["@"]

    assert [w.id for w in worker_email_allowlist_syntax_check(None)] == ["mail.W002"]


def test_a_well_formed_list_is_quiet(settings):
    from core.checks import worker_email_allowlist_syntax_check

    settings.EMAIL_ALLOWED_RECIPIENTS = ["@mozmail.com", ALLOWED]

    assert worker_email_allowlist_syntax_check(None) == []
