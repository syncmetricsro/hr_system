"""CorvinumEU's narrow offer-email enablement (ADR 0029 amendment).

The messaging package is installed for one transport only. These tests make
that split executable: HR Admin/Manager receives offer authoring and sending,
while SMS and every non-manager offer action stay absent or forbidden.
"""

from __future__ import annotations

import pytest
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.urls import NoReverseMatch, reverse

from core.accounts.models import User
from core.people.models import Person
from features.messaging.models import (
    EmailBatch,
    JobOffer,
    OfferEmailKind,
    OfferEmailTemplate,
    OutboundEmail,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.skipif(
        settings.HELP_ASSET_NAMESPACE != "corvinum",
        reason="CorvinumEU client-policy regression",
    ),
]


def _user(role: str) -> User:
    return User.objects.create_user(
        email=f"offer-{role}@demo.corvinum.test", password="x", role=role
    )


def test_manager_sees_offer_navigation_and_can_open_workspace(client):
    client.force_login(_user("manager"))

    response = client.get(reverse("offer_list"))

    assert response.status_code == 200
    assert reverse("offer_list") in response.content.decode()
    assert reverse("offer_create") in response.content.decode()


@pytest.mark.parametrize("role", ("recruiter", "coordinator", "observer"))
def test_non_managers_cannot_see_or_open_offers(client, role):
    client.force_login(_user(role))

    response = client.get(reverse("offer_list"))

    assert response.status_code == 403
    assert (
        reverse("offer_list") not in client.get(reverse("people_list")).content.decode()
    )


def test_manager_gets_single_person_offer_panel_without_sms(client):
    manager = _user("manager")
    person = Person.objects.create(
        first_name="Mira",
        last_name="Novakova",
        email="mira@demo.corvinum.test",
        preferred_language="hu",
    )
    JobOffer.objects.create(title="CNC operátor — demo")
    client.force_login(manager)

    body = client.get(reverse("person_detail", args=[person.pk])).content.decode()

    assert reverse("send_offer_email", args=[person.pk]) in body
    with pytest.raises(NoReverseMatch):
        reverse("send_sms", args=[person.pk])


def test_corvinum_demo_seed_supplies_only_supported_offer_languages():
    call_command("seed_corvinum_demo", verbosity=0)

    assert set(OfferEmailTemplate.objects.values_list("language", flat=True)) == {
        "sk",
        "hu",
    }
    offer = JobOffer.objects.get(title="CNC operátor — demo")
    assert offer.project.code == "CV-ALFA"
    assert offer.office is None


def test_manager_can_confirm_a_no_office_bulk_send_with_no_external_provider(
    client, settings
):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_ALLOWED_RECIPIENTS = [
        "mira@demo.corvinum.test",
        "marek@demo.corvinum.test",
    ]
    mail.outbox.clear()
    manager = _user("manager")
    offer = JobOffer.objects.create(title="CNC operátor — demo")
    OfferEmailTemplate.objects.create(
        kind=OfferEmailKind.NEW_OFFER,
        language="sk",
        subject="Ponuka: $offer_title",
        body="Dobrý deň, $first_name.",
    )
    for first_name, address in (
        ("Mira", "mira@demo.corvinum.test"),
        ("Marek", "marek@demo.corvinum.test"),
    ):
        Person.objects.create(
            first_name=first_name,
            last_name="Demo",
            email=address,
            preferred_language="sk",
        )
    client.force_login(manager)

    response = client.post(
        reverse("offer_send_bulk", args=[offer.pk]),
        {
            "kind": OfferEmailKind.NEW_OFFER,
            "lifecycle_status": "",
            "office": "",
            "confirm": "on",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == reverse("offer_list")
    assert len(mail.outbox) == 2
    assert EmailBatch.objects.get().recipient_count == 2
    assert set(OutboundEmail.objects.values_list("status", flat=True)) == {
        OutboundEmail.Status.SENT
    }
