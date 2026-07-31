"""Uploaded files are reachable only through a permission check.

`/media/` is deliberately unrouted in production, and these views are the only
way in. The design docs originally specified a bare nginx alias, which would
have served every certificate scan to anyone holding the URL — a UUID filename
is obscurity, not authorization. These tests are what stop that from being
reintroduced quietly.

The certificate rule is narrower than the office boundary on purpose: the
*existence* of a certificate is a broad read within the office, but the scan
itself follows `can_view_sensitive`, the rule already settled for DOB and
identifiers.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.apps import apps as django_apps
from django.core.files.base import ContentFile
from django.urls import reverse

from core.offices.models import Office
from core.people.models import LifecycleStatus, Person

if not django_apps.is_installed("features.compliance"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)

from features.compliance.models import Certificate  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

TODAY = dt.date.today()
# Smallest thing Pillow-free code will happily stream; content is irrelevant
# because these views never re-decode, they only authorize and send.
FILE_BYTES = b"not-really-an-image-but-bytes-are-bytes"


@pytest.fixture
def world(django_user_model):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([vm])
    other_recruiter = django_user_model.objects.create_user(
        email="rec2@demo.jober.test", password="x", role="recruiter"
    )
    other_recruiter.offices.set([vm])
    owning_recruiter = django_user_model.objects.create_user(
        email="rec1@demo.jober.test", password="x", role="recruiter"
    )
    owning_recruiter.offices.set([vm])

    mine = Person.objects.create(
        first_name="Olha",
        last_name="VM",
        office=vm,
        owning_recruiter=owning_recruiter,
        lifecycle_status=LifecycleStatus.WORKING,
    )
    theirs = Person.objects.create(
        first_name="Farrukh",
        last_name="Gyor",
        office=gyor,
        lifecycle_status=LifecycleStatus.WORKING,
    )
    for person in (mine, theirs):
        person.avatar.save("a.webp", ContentFile(FILE_BYTES), save=True)

    certificate = Certificate.objects.create(
        person=mine, name="Medical", expiry_date=TODAY + dt.timedelta(days=30)
    )
    certificate.front_document.save("c.pdf", ContentFile(FILE_BYTES), save=True)
    certificate.back_document.save("c.jpg", ContentFile(FILE_BYTES), save=True)
    their_certificate = Certificate.objects.create(
        person=theirs, name="Medical", expiry_date=TODAY + dt.timedelta(days=30)
    )
    their_certificate.front_document.save("c.pdf", ContentFile(FILE_BYTES), save=True)

    return {
        "manager": manager,
        "owning_recruiter": owning_recruiter,
        "other_recruiter": other_recruiter,
        "mine": mine,
        "theirs": theirs,
        "certificate": certificate,
        "their_certificate": their_certificate,
    }


# --- /media/ must stay unrouted -------------------------------------------


def test_media_url_is_not_served(client, world, settings):
    """The whole point: no bare path to the file exists, so adding an nginx
    alias later would be the *only* way to expose one, and that is now
    documented as forbidden rather than merely absent."""
    settings.DEBUG = False
    client.force_login(world["manager"])
    response = client.get(f"/media/{world['mine'].avatar.name}")
    assert response.status_code == 404


# --- avatars ---------------------------------------------------------------


def test_person_avatar_requires_login(client, world):
    response = client.get(reverse("person_avatar_file", args=[world["mine"].pk]))
    assert response.status_code in (302, 403)


def test_person_avatar_served_within_office(client, world):
    client.force_login(world["manager"])
    response = client.get(reverse("person_avatar_file", args=[world["mine"].pk]))
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == FILE_BYTES
    assert "private" in response["Cache-Control"]


def test_person_avatar_blocked_across_offices(client, world):
    client.force_login(world["manager"])
    response = client.get(reverse("person_avatar_file", args=[world["theirs"].pk]))
    assert response.status_code == 403


def test_missing_file_404s_rather_than_500s(client, world):
    """A database restored without the media volume must not crash every page
    that embeds an avatar."""
    world["mine"].avatar.storage.delete(world["mine"].avatar.name)
    client.force_login(world["manager"])
    response = client.get(reverse("person_avatar_file", args=[world["mine"].pk]))
    assert response.status_code == 404


# --- certificate documents -------------------------------------------------


def test_certificate_document_served_to_manager(client, world):
    client.force_login(world["manager"])
    response = client.get(
        reverse("certificate_document", args=[world["certificate"].pk])
    )
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == FILE_BYTES


def test_certificate_document_served_to_owning_recruiter(client, world):
    client.force_login(world["owning_recruiter"])
    response = client.get(
        reverse("certificate_document", args=[world["certificate"].pk])
    )
    assert response.status_code == 200


def test_certificate_document_hidden_from_unconnected_recruiter(client, world):
    """Same office, but no relationship to this person: may see that the
    certificate exists, may not open the scan."""
    client.force_login(world["other_recruiter"])
    response = client.get(
        reverse("certificate_document", args=[world["certificate"].pk])
    )
    assert response.status_code == 403


def test_certificate_document_blocked_across_offices(client, world):
    client.force_login(world["manager"])
    response = client.get(
        reverse("certificate_document", args=[world["their_certificate"].pk])
    )
    assert response.status_code == 403


def test_certificate_back_document_is_served_with_the_same_policy(client, world):
    client.force_login(world["manager"])
    response = client.get(
        reverse("certificate_back_document", args=[world["certificate"].pk])
    )
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == FILE_BYTES
