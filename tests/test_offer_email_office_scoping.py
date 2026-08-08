"""Offer-email views must 403 across the office boundary (ADR 0026).

The same lesson `test_object_view_office_scoping.py` records: filtering a list
never stops someone typing another office's pk into a URL. Offer emails add two
new shapes of that mistake — an offer *object* (which carries its own office,
not a person's), and a bulk send whose recipient query is itself the boundary.
A bulk send that scoped its preview but not its execution would be the worst
version: the manager sees ten names and emails four hundred.

Request-level through `client` on purpose. `assert_office_in_scope` and
`scope_people` are already correct; what a unit test cannot catch is a view
that forgets to call them.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.core import mail
from django.urls import reverse

from core.offices.models import Office
from core.people.models import LifecycleStatus, Person

if not django_apps.is_installed("features.messaging"):
    pytest.skip("Messaging feature not installed", allow_module_level=True)

from features.messaging.models import (  # noqa: E402
    EmailBatch,
    JobOffer,
    OfferEmailKind,
    OfferEmailTemplate,
    OutboundEmail,
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture(autouse=True)
def _locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    mail.outbox.clear()
    return settings


@pytest.fixture
def two_offices(django_user_model, settings):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([vm])
    observer = django_user_model.objects.create_user(
        email="obs@demo.jober.test", password="x", role="observer"
    )
    superuser = django_user_model.objects.create_superuser(
        email="root@demo.jober.test", password="x"
    )

    OfferEmailTemplate.objects.create(
        kind=OfferEmailKind.NEW_OFFER,
        language=settings.LANGUAGE_CODE,
        subject="Offer: $offer_title",
        body="Hello $first_name",
    )
    return {
        "vm": vm,
        "gyor": gyor,
        "manager": manager,
        "observer": observer,
        "superuser": superuser,
        "mine": Person.objects.create(
            first_name="Olha",
            last_name="VM",
            office=vm,
            email="olha@demo.jober.test",
            lifecycle_status=LifecycleStatus.WORKING,
        ),
        "theirs": Person.objects.create(
            first_name="Farrukh",
            last_name="Gyor",
            office=gyor,
            email="farrukh@demo.jober.test",
            lifecycle_status=LifecycleStatus.WORKING,
        ),
        "my_offer": JobOffer.objects.create(title="VM offer", office=vm),
        "their_offer": JobOffer.objects.create(title="Győr offer", office=gyor),
    }


# --- the per-person send ---------------------------------------------------


def test_offer_email_to_another_office_is_forbidden(client, two_offices):
    client.force_login(two_offices["manager"])

    response = client.post(
        reverse("send_offer_email", args=[two_offices["theirs"].pk]),
        {"offer": two_offices["my_offer"].pk, "kind": OfferEmailKind.NEW_OFFER},
    )

    assert response.status_code == 403
    assert OutboundEmail.objects.count() == 0
    assert mail.outbox == []


def test_offer_email_within_own_office_is_allowed(client, two_offices):
    """The guard rejects the *other* office, not everything — one account
    seeing less proves nothing on its own."""
    client.force_login(two_offices["manager"])

    response = client.post(
        reverse("send_offer_email", args=[two_offices["mine"].pk]),
        {"offer": two_offices["my_offer"].pk, "kind": OfferEmailKind.NEW_OFFER},
    )

    assert response.status_code == 302
    assert OutboundEmail.objects.get().status == OutboundEmail.Status.SENT


def test_another_offices_offer_cannot_be_used(client, two_offices):
    """The person is in scope but the *offer* is not. Both sides of the form
    are a boundary."""
    client.force_login(two_offices["manager"])

    client.post(
        reverse("send_offer_email", args=[two_offices["mine"].pk]),
        {"offer": two_offices["their_offer"].pk, "kind": OfferEmailKind.NEW_OFFER},
    )

    assert OutboundEmail.objects.count() == 0
    assert mail.outbox == []


def test_unrestricted_role_is_not_blocked(client, two_offices):
    client.force_login(two_offices["superuser"])

    response = client.post(
        reverse("send_offer_email", args=[two_offices["theirs"].pk]),
        {"offer": two_offices["their_offer"].pk, "kind": OfferEmailKind.NEW_OFFER},
    )

    assert response.status_code == 302


# --- offer objects ---------------------------------------------------------


def test_editing_another_offices_offer_is_forbidden(client, two_offices):
    client.force_login(two_offices["manager"])
    response = client.get(reverse("offer_edit", args=[two_offices["their_offer"].pk]))
    assert response.status_code == 403


def test_editing_own_offer_is_allowed(client, two_offices):
    client.force_login(two_offices["manager"])
    response = client.get(reverse("offer_edit", args=[two_offices["my_offer"].pk]))
    assert response.status_code == 200


def test_closing_another_offices_offer_is_forbidden(client, two_offices):
    client.force_login(two_offices["manager"])

    response = client.post(
        reverse("offer_archive", args=[two_offices["their_offer"].pk])
    )

    assert response.status_code == 403
    two_offices["their_offer"].refresh_from_db()
    assert two_offices["their_offer"].is_active is True


def test_offer_list_shows_only_my_offices(client, two_offices):
    client.force_login(two_offices["manager"])
    response = client.get(reverse("offer_list"))
    titles = [offer.title for offer in response.context["offers"]]
    assert titles == ["VM offer"]


# --- bulk send -------------------------------------------------------------


def test_bulk_send_on_another_offices_offer_is_forbidden(client, two_offices):
    client.force_login(two_offices["manager"])
    response = client.get(
        reverse("offer_send_bulk", args=[two_offices["their_offer"].pk])
    )
    assert response.status_code == 403


def test_bulk_result_for_another_office_is_forbidden(client, two_offices):
    batch = EmailBatch.objects.create(
        offer=two_offices["their_offer"], kind=OfferEmailKind.NEW_OFFER
    )
    client.force_login(two_offices["manager"])

    response = client.get(reverse("offer_batch_detail", args=[batch.pk]))

    assert response.status_code == 403


def test_orphaned_bulk_result_without_office_evidence_fails_closed(client, two_offices):
    batch = EmailBatch.objects.create(offer=None, kind=OfferEmailKind.NEW_OFFER)
    client.force_login(two_offices["manager"])

    response = client.get(reverse("offer_batch_detail", args=[batch.pk]))

    assert response.status_code == 403


def test_bulk_recipients_are_office_scoped(client, two_offices):
    client.force_login(two_offices["manager"])

    response = client.get(reverse("offer_send_bulk", args=[two_offices["my_offer"].pk]))

    assert response.status_code == 200
    assert [row["person"] for row in response.context["rows"]] == [two_offices["mine"]]


def test_bulk_execution_is_scoped_too_not_just_the_preview(client, two_offices):
    """The failure mode worth naming: a preview that scopes and an execution
    that does not."""
    client.force_login(two_offices["manager"])

    preview = client.post(
        reverse("offer_send_bulk", args=[two_offices["my_offer"].pk]),
        {
            "kind": OfferEmailKind.NEW_OFFER,
            "lifecycle_status": "",
            "office": "",
            "q": "",
            "recipients": [two_offices["mine"].pk],
        },
    )
    token = preview.context["form"].initial["preview_token"]
    response = client.post(
        reverse("offer_send_bulk_confirm", args=[two_offices["my_offer"].pk]),
        {"preview_token": token, "confirm": "on"},
    )

    assert response.status_code == 302
    assert [message.to for message in mail.outbox] == [["olha@demo.jober.test"]]


def test_bulk_send_requires_the_confirm_box(client, two_offices):
    client.force_login(two_offices["manager"])

    preview = client.post(
        reverse("offer_send_bulk", args=[two_offices["my_offer"].pk]),
        {
            "kind": OfferEmailKind.NEW_OFFER,
            "lifecycle_status": "",
            "office": "",
            "q": "",
            "recipients": [two_offices["mine"].pk],
        },
    )
    client.post(
        reverse("offer_send_bulk_confirm", args=[two_offices["my_offer"].pk]),
        {"preview_token": preview.context["form"].initial["preview_token"]},
    )

    assert mail.outbox == []


def test_recruiter_may_not_bulk_send(client, two_offices, django_user_model):
    """Per-person sending is a recruiter's job; a campaign is not."""
    recruiter = django_user_model.objects.create_user(
        email="rec@demo.jober.test", password="x", role="recruiter"
    )
    recruiter.offices.set([two_offices["vm"]])
    client.force_login(recruiter)

    response = client.get(reverse("offer_send_bulk", args=[two_offices["my_offer"].pk]))

    assert response.status_code == 403


def test_recruiter_may_not_author_offers(client, two_offices, django_user_model):
    recruiter = django_user_model.objects.create_user(
        email="rec2@demo.jober.test", password="x", role="recruiter"
    )
    recruiter.offices.set([two_offices["vm"]])
    client.force_login(recruiter)

    assert client.get(reverse("offer_list")).status_code == 403
    assert client.get(reverse("offer_create")).status_code == 403


def test_observer_may_not_send(client, two_offices):
    """Observer spans every office by role bypass, which makes it exactly the
    account that must not be able to email anyone."""
    client.force_login(two_offices["observer"])

    response = client.post(
        reverse("send_offer_email", args=[two_offices["mine"].pk]),
        {"offer": two_offices["my_offer"].pk, "kind": OfferEmailKind.NEW_OFFER},
    )

    assert response.status_code == 403
    assert mail.outbox == []
