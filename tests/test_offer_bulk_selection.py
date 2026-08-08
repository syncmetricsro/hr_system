"""Explicit recipient selection, signed review, and idempotent offer batches."""

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
def _email(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    settings.OFFER_EMAIL_BATCH_LIMIT = 100
    settings.OFFER_EMAIL_PREVIEW_MAX_AGE = 900
    mail.outbox.clear()
    return settings


@pytest.fixture
def bulk_data(django_user_model):
    office = Office.objects.create(name="Bratislava", code="BA", country="SK")
    other_office = Office.objects.create(name="Győr", code="GYR", country="HU")
    manager = django_user_model.objects.create_user(
        email="manager@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([office])
    second_manager = django_user_model.objects.create_user(
        email="other-manager@demo.jober.test", password="x", role="manager"
    )
    second_manager.offices.set([office])
    offer = JobOffer.objects.create(title="Demo offer", office=office)
    for language in ("sk", "hu", "uk"):
        OfferEmailTemplate.objects.create(
            kind=OfferEmailKind.NEW_OFFER,
            language=language,
            subject=f"{language}: $first_name",
            body=f"{language} body for $offer_title",
        )
    people = {
        "sk": Person.objects.create(
            first_name="Ágnes",
            last_name="Őri",
            office=office,
            email="agnes@demo.jober.test",
            preferred_language="sk",
            lifecycle_status=LifecycleStatus.AVAILABLE,
        ),
        "hu": Person.objects.create(
            first_name="Eszter",
            last_name="Varga",
            office=office,
            email="eszter@demo.jober.test",
            preferred_language="hu",
            lifecycle_status=LifecycleStatus.WORKING,
        ),
        "uk": Person.objects.create(
            first_name="Olha",
            last_name="Kovalenko",
            office=office,
            email="olha@demo.jober.test",
            preferred_language="uk",
            lifecycle_status=LifecycleStatus.WORKING,
        ),
        "outside": Person.objects.create(
            first_name="Farrukh",
            last_name="Demo",
            office=other_office,
            email="farrukh@demo.jober.test",
        ),
    }
    return {
        "office": office,
        "other_office": other_office,
        "manager": manager,
        "second_manager": second_manager,
        "offer": offer,
        **people,
    }


def _selection(*people, kind=OfferEmailKind.NEW_OFFER, **filters):
    return {
        "kind": kind,
        "lifecycle_status": filters.get("lifecycle_status", ""),
        "office": filters.get("office", ""),
        "q": filters.get("q", ""),
        "recipients": [person.pk for person in people],
    }


def _preview(client, data, *people):
    response = client.post(
        reverse("offer_send_bulk", args=[data["offer"].pk]),
        _selection(*people),
    )
    assert response.status_code == 200
    assert response.template_name == "pages/offer_send_bulk_preview.html"
    return response.context["form"].initial["preview_token"], response


def _confirm(client, data, token, *, reviewed=True):
    payload = {"preview_token": token}
    if reviewed:
        payload["confirm"] = "on"
    return client.post(
        reverse("offer_send_bulk_confirm", args=[data["offer"].pk]), payload
    )


def test_picker_shows_blocked_contacts_but_never_selects_anyone_by_default(
    client, bulk_data, settings
):
    missing = Person.objects.create(
        first_name="No", last_name="Email", office=bulk_data["office"]
    )
    opted_out = Person.objects.create(
        first_name="Opted",
        last_name="Out",
        office=bulk_data["office"],
        email="optout@demo.jober.test",
        email_opt_out=True,
    )
    blacklisted = Person.objects.create(
        first_name="Blocked",
        last_name="Person",
        office=bulk_data["office"],
        email="blocked@demo.jober.test",
        lifecycle_status=LifecycleStatus.BLACKLISTED,
    )
    settings.EMAIL_ALLOWED_RECIPIENTS = [bulk_data["sk"].email]
    client.force_login(bulk_data["manager"])

    response = client.get(reverse("offer_send_bulk", args=[bulk_data["offer"].pk]))

    rows = {row["person"].pk: row for row in response.context["rows"]}
    assert rows[bulk_data["sk"].pk]["eligible"] is True
    for person in (missing, opted_out, blacklisted, bulk_data["hu"], bulk_data["uk"]):
        assert rows[person.pk]["eligible"] is False
        assert rows[person.pk]["reason"]
    assert bulk_data["outside"].pk not in rows
    assert 'name="recipients"' in response.content.decode()
    assert 'name="recipients" checked' not in response.content.decode()


def test_archived_people_are_absent_and_filters_cover_status_email_and_folded_name(
    client, bulk_data
):
    archived = Person.objects.create(
        first_name="Archived",
        last_name="Worker",
        office=bulk_data["office"],
        email="archived@demo.jober.test",
        is_archived=True,
    )
    client.force_login(bulk_data["manager"])
    url = reverse("offer_send_bulk", args=[bulk_data["offer"].pk])

    response = client.get(url, {"q": "agnes ori"})
    assert [row["person"] for row in response.context["rows"]] == [bulk_data["sk"]]

    response = client.get(url, {"q": "eszter@demo", "lifecycle_status": "working"})
    assert [row["person"] for row in response.context["rows"]] == [bulk_data["hu"]]

    response = client.get(url)
    assert archived.pk not in {row["person"].pk for row in response.context["rows"]}


def test_empty_out_of_scope_and_over_limit_selections_send_nothing(
    client, bulk_data, settings
):
    client.force_login(bulk_data["manager"])
    url = reverse("offer_send_bulk", args=[bulk_data["offer"].pk])

    empty = client.post(url, _selection())
    assert empty.status_code == 200
    assert empty.context["form"].errors["recipients"]

    outside = client.post(url, _selection(bulk_data["outside"]))
    assert outside.status_code == 200
    assert outside.context["form"].errors["recipients"]

    settings.OFFER_EMAIL_BATCH_LIMIT = 2
    excessive = client.post(
        url, _selection(bulk_data["sk"], bulk_data["hu"], bulk_data["uk"])
    )
    assert excessive.status_code == 200
    assert excessive.context["form"].errors["recipients"]
    assert EmailBatch.objects.count() == 0
    assert mail.outbox == []


@pytest.mark.parametrize("missing", ("smtp", "template"))
def test_unavailable_delivery_configuration_disables_progression(
    client, bulk_data, settings, missing
):
    if missing == "smtp":
        settings.EMAIL_BACKEND = ""
    else:
        OfferEmailTemplate.objects.filter(kind=OfferEmailKind.NEW_OFFER).delete()
    client.force_login(bulk_data["manager"])
    url = reverse("offer_send_bulk", args=[bulk_data["offer"].pk])

    response = client.get(url)
    submission = client.post(url, _selection(bulk_data["sk"]))

    assert response.status_code == 200
    assert "disabled" in response.content.decode()
    assert submission.status_code == 200
    assert submission.template_name == "pages/offer_send_bulk.html"
    assert EmailBatch.objects.count() == 0
    assert mail.outbox == []


def test_preview_lists_exact_recipients_and_one_example_per_language(client, bulk_data):
    client.force_login(bulk_data["manager"])

    _token, response = _preview(
        client, bulk_data, bulk_data["sk"], bulk_data["hu"], bulk_data["uk"]
    )

    assert {person.pk for person in response.context["selected"]} == {
        bulk_data["sk"].pk,
        bulk_data["hu"].pk,
        bulk_data["uk"].pk,
    }
    assert {preview["language"] for preview in response.context["previews"]} == {
        "sk",
        "hu",
        "uk",
    }
    assert EmailBatch.objects.count() == 0
    assert mail.outbox == []


@pytest.mark.parametrize("mutation", ("tamper", "other_actor", "expired"))
def test_preview_token_rejects_tampering_other_users_and_expiry(
    client, bulk_data, settings, mutation
):
    client.force_login(bulk_data["manager"])
    token, _response = _preview(client, bulk_data, bulk_data["sk"])
    if mutation == "tamper":
        token += "x"
    elif mutation == "other_actor":
        client.force_login(bulk_data["second_manager"])
    else:
        settings.OFFER_EMAIL_PREVIEW_MAX_AGE = -1

    response = _confirm(client, bulk_data, token)

    assert response.status_code == 302
    assert response.headers["Location"] == reverse(
        "offer_send_bulk", args=[bulk_data["offer"].pk]
    )
    assert EmailBatch.objects.count() == 0
    assert mail.outbox == []


def test_state_change_after_preview_aborts_the_entire_batch(client, bulk_data):
    client.force_login(bulk_data["manager"])
    token, _response = _preview(client, bulk_data, bulk_data["sk"], bulk_data["hu"])
    bulk_data["hu"].email_opt_out = True
    bulk_data["hu"].save(update_fields=["email_opt_out"])

    response = _confirm(client, bulk_data, token)

    assert response.status_code == 302
    assert EmailBatch.objects.count() == 0
    assert mail.outbox == []


def test_confirmation_requires_review_and_is_idempotent(client, bulk_data):
    client.force_login(bulk_data["manager"])
    token, _response = _preview(client, bulk_data, bulk_data["sk"], bulk_data["hu"])

    not_reviewed = _confirm(client, bulk_data, token, reviewed=False)
    assert not_reviewed.status_code == 302
    assert EmailBatch.objects.count() == 0

    first = _confirm(client, bulk_data, token)
    batch = EmailBatch.objects.get()
    second = _confirm(client, bulk_data, token)

    expected = reverse("offer_batch_detail", args=[batch.pk])
    assert first.headers["Location"] == expected
    assert second.headers["Location"] == expected
    assert batch.recipient_count == 2
    assert len(mail.outbox) == 2
    assert OutboundEmail.objects.filter(batch=batch).count() == 2


def test_result_page_reports_each_recorded_outcome(client, bulk_data):
    client.force_login(bulk_data["manager"])
    batch = EmailBatch.objects.create(
        offer=bulk_data["offer"],
        kind=OfferEmailKind.NEW_OFFER,
        recipient_count=3,
        created_by=bulk_data["manager"],
    )
    for person, status in (
        (bulk_data["sk"], OutboundEmail.Status.SENT),
        (bulk_data["hu"], OutboundEmail.Status.FAILED),
        (bulk_data["uk"], OutboundEmail.Status.BLOCKED),
    ):
        OutboundEmail.objects.create(
            batch=batch,
            offer=bulk_data["offer"],
            person=person,
            kind=OfferEmailKind.NEW_OFFER,
            to_email=person.email,
            status=status,
        )

    response = client.get(reverse("offer_batch_detail", args=[batch.pk]))

    assert response.status_code == 200
    assert response.context["sent_count"] == 1
    assert response.context["failed_count"] == 1
    assert response.context["blocked_count"] == 1
    assert len(response.context["emails"]) == 3


@pytest.mark.parametrize("role", ("recruiter", "coordinator", "observer"))
def test_non_managers_cannot_open_selection_confirmation_or_results(
    client, bulk_data, django_user_model, role
):
    user = django_user_model.objects.create_user(
        email=f"{role}@demo.jober.test", password="x", role=role
    )
    user.offices.set([bulk_data["office"]])
    batch = EmailBatch.objects.create(
        offer=bulk_data["offer"], kind=OfferEmailKind.NEW_OFFER
    )
    client.force_login(user)

    assert (
        client.get(reverse("offer_send_bulk", args=[bulk_data["offer"].pk])).status_code
        == 403
    )
    assert (
        client.post(
            reverse("offer_send_bulk_confirm", args=[bulk_data["offer"].pk]), {}
        ).status_code
        == 403
    )
    assert client.get(reverse("offer_batch_detail", args=[batch.pk])).status_code == 403
