"""Views that take an object pk must 403 across the office boundary.

ADR 0026 Phase B scoped the *list* queries in messaging, compliance and
feedback but left their per-object views fetching by pk, so a Velký Meder
manager could text a Győr worker, edit or delete that worker's certificates,
and download another office's feedback flyer by POSTing or GETting a pk.
Filtering a list never stops someone typing a URL - that is the whole reason
`core.offices.scoping.assert_person_in_scope` exists.

These are deliberately end-to-end through the client rather than unit tests on
the guard: the guard was already written and correct; what was missing was
calling it, which only a request-level test catches.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.apps import apps as django_apps
from django.urls import reverse

from core.offices.models import Office
from core.people.models import LifecycleStatus, Person

if not django_apps.is_installed("features.compliance"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)

from features.compliance.models import Certificate  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

TODAY = dt.date.today()


@pytest.fixture
def offices(django_user_model):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([vm])
    observer = django_user_model.objects.create_user(
        email="obs@demo.jober.test", password="x", role="observer"
    )

    mine = Person.objects.create(
        first_name="Olha",
        last_name="VM",
        office=vm,
        phone="+421900000001",
        lifecycle_status=LifecycleStatus.WORKING,
    )
    theirs = Person.objects.create(
        first_name="Farrukh",
        last_name="Gyor",
        office=gyor,
        phone="+421900000002",
        lifecycle_status=LifecycleStatus.WORKING,
    )
    return {
        "vm": vm,
        "gyor": gyor,
        "manager": manager,
        "observer": observer,
        "mine": mine,
        "theirs": theirs,
    }


def _certificate(person: Person) -> Certificate:
    return Certificate.objects.create(
        person=person,
        category="FORKLIFT",
        name="Forklift licence",
        expiry_date=TODAY + dt.timedelta(days=30),
    )


# --- messaging -------------------------------------------------------------


def test_sms_to_another_office_is_forbidden(client, offices, settings):
    client.force_login(offices["manager"])
    response = client.post(
        reverse("send_sms", args=[offices["theirs"].pk]), {"body": "hello"}
    )
    assert response.status_code == 403


def test_sms_within_own_office_is_allowed(client, offices):
    """Guard rejects the *other* office, not everything. Twilio is
    unconfigured under test, so the send is recorded failed - what matters
    here is that the request was authorised (a redirect, not a 403)."""
    client.force_login(offices["manager"])
    response = client.post(
        reverse("send_sms", args=[offices["mine"].pk]), {"body": "hello"}
    )
    assert response.status_code == 302


def test_unrestricted_actor_is_not_blocked_by_the_office_guard(
    client, offices, django_user_model
):
    """`user_office_scope` returns its unrestricted sentinel for superusers,
    and the guard must honour that. Observer is not usable here: it is denied
    `sms.send` outright by the action gate, so a 403 would prove nothing about
    the office boundary."""
    root = django_user_model.objects.create_superuser(
        email="root@demo.jober.test", password="x"
    )
    client.force_login(root)
    response = client.post(
        reverse("send_sms", args=[offices["theirs"].pk]), {"body": "hello"}
    )
    assert response.status_code == 302


# --- compliance ------------------------------------------------------------


def test_certificate_create_for_another_office_is_forbidden(client, offices):
    client.force_login(offices["manager"])
    response = client.get(reverse("certificate_create", args=[offices["theirs"].pk]))
    assert response.status_code == 403


def test_certificate_edit_in_another_office_is_forbidden(client, offices):
    certificate = _certificate(offices["theirs"])
    client.force_login(offices["manager"])
    response = client.get(reverse("certificate_edit", args=[certificate.pk]))
    assert response.status_code == 403


def test_certificate_archive_in_another_office_is_forbidden(client, offices):
    certificate = _certificate(offices["theirs"])
    client.force_login(offices["manager"])
    response = client.post(
        reverse("certificate_archive", args=[certificate.pk]), {"reason": "No"}
    )
    assert response.status_code == 403
    assert Certificate.objects.filter(pk=certificate.pk).exists()


def test_certificate_edit_in_own_office_still_works(client, offices):
    certificate = _certificate(offices["mine"])
    client.force_login(offices["manager"])
    response = client.get(reverse("certificate_edit", args=[certificate.pk]))
    assert response.status_code == 200
