"""Offer emails: language selection, rendering, and batching.

The language behaviour is the reason this feature exists in the shape it does.
`seed_messaging` records the gap it could not close: SMS sends `template.body`
verbatim, so a worker gets Slovak whatever their `preferred_language` says.
Offer emails are long-form, which makes the same compromise much worse, so the
templates are keyed `(kind, language)` and the send picks the row. These tests
pin the picking — including the fallbacks, which is where a free-text
`preferred_language` column will otherwise produce a 500 in front of a manager.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.core import mail
from django.utils import translation

if not django_apps.is_installed("features.messaging"):
    pytest.skip("Messaging feature not installed", allow_module_level=True)

from core.people.models import Person  # noqa: E402
from features.messaging.models import (  # noqa: E402
    EmailBatch,
    JobOffer,
    OfferEmailKind,
    OfferEmailTemplate,
    OutboundEmail,
)
from features.messaging.services import (  # noqa: E402
    OfferBatchTooLarge,
    OfferTemplateMissing,
    render_offer_email,
    send_offer_batch,
    send_offer_email,
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture(autouse=True)
def _locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    mail.outbox.clear()
    return settings


@pytest.fixture
def offer():
    return JobOffer.objects.create(
        title="Operátor výroby",
        location="Velký Meder",
        wage="8.50",
        wage_unit=JobOffer.WageUnit.HOUR,
        currency="EUR",
    )


def _template(language, subject="S: $offer_title", body="B: $first_name"):
    return OfferEmailTemplate.objects.create(
        kind=OfferEmailKind.NEW_OFFER,
        language=language,
        subject=subject,
        body=body,
    )


def _person(language="", **kwargs):
    kwargs.setdefault("first_name", "Oksana")
    kwargs.setdefault("last_name", "Kovalenko")
    kwargs.setdefault("email", "oksana@demo.jober.test")
    return Person.objects.create(preferred_language=language, **kwargs)


# --- language selection ----------------------------------------------------


def test_worker_gets_their_own_language(offer):
    _template("sk", body="Slovak")
    _template("uk", body="Ukrainian")

    language, _subject, body = render_offer_email(
        offer, _person("uk"), OfferEmailKind.NEW_OFFER
    )

    assert language == "uk"
    assert body == "Ukrainian"


def test_unknown_preferred_language_falls_back_to_the_site_default(offer, settings):
    """`preferred_language` is a free CharField with no choices validation, so
    an unusable value must degrade to the default rather than fail the send."""
    _template(settings.LANGUAGE_CODE, body="Default")

    language, _subject, body = render_offer_email(
        offer, _person("klingon"), OfferEmailKind.NEW_OFFER
    )

    assert language == settings.LANGUAGE_CODE
    assert body == "Default"


def test_blank_preferred_language_falls_back(offer, settings):
    _template(settings.LANGUAGE_CODE, body="Default")
    _language, _subject, body = render_offer_email(
        offer, _person(""), OfferEmailKind.NEW_OFFER
    )
    assert body == "Default"


def test_any_active_template_beats_sending_nothing(offer):
    """Neither the worker's language nor the site default exists, but a
    Hungarian row does. A wrong-language offer is recoverable; silence is not."""
    _template("hu", body="Hungarian")
    _language, _subject, body = render_offer_email(
        offer, _person("uk"), OfferEmailKind.NEW_OFFER
    )
    assert body == "Hungarian"


def test_inactive_templates_are_not_picked(offer, settings):
    template = _template(settings.LANGUAGE_CODE)
    template.is_active = False
    template.save(update_fields=["is_active"])

    with pytest.raises(OfferTemplateMissing):
        render_offer_email(offer, _person(), OfferEmailKind.NEW_OFFER)


def test_missing_template_records_failed_rather_than_raising(offer):
    """A manager pressing Send with no template must get an error, not a 500."""
    record = send_offer_email(offer, _person(), OfferEmailKind.NEW_OFFER)

    assert record.status == OutboundEmail.Status.FAILED
    assert mail.outbox == []


# --- placeholder substitution ----------------------------------------------


def test_placeholders_are_substituted(offer):
    _template("en", subject="Offer: $offer_title", body="Hello $first_name, $wage.")

    _language, subject, body = render_offer_email(
        offer, _person("en"), OfferEmailKind.NEW_OFFER
    )

    assert subject == "Offer: Operátor výroby"
    assert body == "Hello Oksana, 8.50 EUR per hour."


def test_the_wage_unit_follows_the_recipient_not_the_sender(offer):
    """`get_wage_unit_display()` resolves against the *active* locale, which
    during a send is the sending staff member's. Without an override a
    Ukrainian worker's offer read "8.50 EUR za hodinu" — Ukrainian body, Slovak
    wage unit — because the sender happened to be working in Slovak."""
    _template("uk", body="$wage")

    with translation.override("sk"):  # the sender's UI language
        _language, _subject, body = render_offer_email(
            offer, _person("uk"), OfferEmailKind.NEW_OFFER
        )

    assert body == "8.50 EUR за годину"


def test_an_unknown_token_is_left_intact(offer, settings):
    """`safe_substitute`, not Django template rendering: a typo in an
    operator-authored body must not raise halfway through a batch."""
    _template(settings.LANGUAGE_CODE, body="Hello $frist_name")

    _language, _subject, body = render_offer_email(
        offer, _person(), OfferEmailKind.NEW_OFFER
    )

    assert body == "Hello $frist_name"


def test_empty_optional_fields_do_not_render_as_none(settings):
    """A worker reading "Starts: None" is a bug, not a blank."""
    bare = JobOffer.objects.create(title="Skladník")
    _template(settings.LANGUAGE_CODE, body="Starts: $start_date|Wage: $wage|")

    _language, _subject, body = render_offer_email(
        bare, _person(), OfferEmailKind.NEW_OFFER
    )

    assert body == "Starts: |Wage: |"


# --- one send --------------------------------------------------------------


def test_a_successful_send_stores_what_was_sent(offer, settings):
    _template(settings.LANGUAGE_CODE, subject="Offer: $offer_title", body="Hi")

    record = send_offer_email(offer, _person(), OfferEmailKind.NEW_OFFER)

    assert record.status == OutboundEmail.Status.SENT
    assert record.subject == "Offer: Operátor výroby"
    assert record.language == settings.LANGUAGE_CODE
    assert record.to_email == "oksana@demo.jober.test"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Offer: Operátor výroby"


def test_every_outcome_is_recorded(offer):
    """No template, so nothing is sent — but the attempt is still evidence."""
    send_offer_email(offer, _person(), OfferEmailKind.NEW_OFFER)
    assert OutboundEmail.objects.count() == 1


# --- batches ---------------------------------------------------------------


def test_a_batch_sends_one_email_per_person(offer, settings):
    _template(settings.LANGUAGE_CODE)
    people = [
        _person(email=f"worker{index}@demo.jober.test", first_name=f"W{index}")
        for index in range(3)
    ]

    batch = send_offer_batch(offer, people, OfferEmailKind.NEW_OFFER)

    assert batch.recipient_count == 3
    assert len(mail.outbox) == 3
    assert OutboundEmail.objects.filter(batch=batch).count() == 3


def test_an_over_limit_batch_is_rejected_instead_of_truncated(offer, settings):
    """A blast-radius limit, not a business rule: a mis-filtered recipient query
    must not become a thousand emails in one POST."""
    settings.OFFER_EMAIL_BATCH_LIMIT = 2
    _template(settings.LANGUAGE_CODE)
    people = [
        _person(email=f"worker{index}@demo.jober.test", first_name=f"W{index}")
        for index in range(5)
    ]

    with pytest.raises(OfferBatchTooLarge):
        send_offer_batch(offer, people, OfferEmailKind.NEW_OFFER)

    assert EmailBatch.objects.count() == 0
    assert mail.outbox == []


def test_one_blocked_recipient_does_not_stop_the_batch(offer, settings):
    _template(settings.LANGUAGE_CODE)
    good = _person(email="good@demo.jober.test")
    opted_out = _person(email="stop@demo.jober.test", email_opt_out=True)
    also_good = _person(email="fine@demo.jober.test")

    batch = send_offer_batch(
        offer, [good, opted_out, also_good], OfferEmailKind.NEW_OFFER
    )

    assert len(mail.outbox) == 2
    assert (
        OutboundEmail.objects.filter(
            batch=batch, status=OutboundEmail.Status.BLOCKED
        ).count()
        == 1
    )


def test_a_batch_row_exists_even_when_nobody_is_sendable(offer, settings):
    _template(settings.LANGUAGE_CODE)
    batch = send_offer_batch(offer, [], OfferEmailKind.NEW_OFFER)
    assert EmailBatch.objects.filter(pk=batch.pk).exists()
    assert batch.recipient_count == 0
