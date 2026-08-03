"""The offer-email seed must leave the feature usable, in three languages.

`test_sms_templates_seed.py` records why this matters: the SMS picker was
rendered behind `{% if panel.message_templates %}`, nothing seeded templates,
so the control never appeared and the runbook's "pick a template" step had
nothing to pick. The offer panel has the same shape, plus a harder failure — a
send with no template for the worker's language records FAILED rather than
silently sending English.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.core.management import call_command

from core.offices.models import Office

if not django_apps.is_installed("features.messaging"):
    pytest.skip("Messaging feature not installed", allow_module_level=True)

from features.messaging.models import (  # noqa: E402
    JobOffer,
    OfferEmailKind,
    OfferEmailTemplate,
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


def test_seed_creates_templates_for_every_worker_language():
    call_command("seed_offer_emails")

    languages = set(
        OfferEmailTemplate.objects.filter(kind=OfferEmailKind.NEW_OFFER).values_list(
            "language", flat=True
        )
    )

    assert {"sk", "hu", "uk"} <= languages


def test_every_kind_is_seeded():
    """A kind offered in the send form with no template behind it is a dead
    option that only reveals itself as a FAILED record."""
    call_command("seed_offer_emails")

    seeded = set(OfferEmailTemplate.objects.values_list("kind", flat=True))

    assert seeded == {kind for kind, _label in OfferEmailKind.choices}


def test_seed_is_idempotent():
    call_command("seed_offer_emails")
    first = OfferEmailTemplate.objects.count()

    call_command("seed_offer_emails")

    assert OfferEmailTemplate.objects.count() == first


def test_reseeding_repairs_a_hand_edited_body():
    call_command("seed_offer_emails")
    template = OfferEmailTemplate.objects.filter(language="sk").first()
    original = template.body
    template.body = "someone typed over this in admin"
    template.is_active = False
    template.save(update_fields=["body", "is_active"])

    call_command("seed_offer_emails")

    template.refresh_from_db()
    assert template.body == original
    assert template.is_active is True


def test_seeded_bodies_carry_placeholders():
    """A template with no placeholders would send every worker an identical,
    unaddressed letter — which reads as spam and defeats the feature."""
    call_command("seed_offer_emails")

    for template in OfferEmailTemplate.objects.all():
        assert "$first_name" in template.body or "$offer_title" in template.body


def test_seed_offers_something_to_send():
    call_command("seed_offer_emails")
    assert JobOffer.objects.filter(is_active=True).exists()


def test_seeded_offers_carry_an_office_when_offices_exist():
    """Unlike a Person, an office-less offer has no owning-recruiter fallback:
    it is visible to unrestricted roles only. A seeded offer that every manager
    is scoped out of looks exactly like a broken feature — which is how the
    first e2e run failed."""
    Office.objects.create(name="Velký Meder", code="VM", country="SK")

    call_command("seed_offer_emails")

    assert not JobOffer.objects.filter(office__isnull=True).exists()


def test_seed_survives_an_empty_project_table():
    """CorvinumEU populates no offices and a bare test DB has no projects; the
    seed must not depend on either."""
    call_command("seed_offer_emails")
    assert JobOffer.objects.exists()
