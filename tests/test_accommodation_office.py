from __future__ import annotations

import pytest

from core.offices.models import Office
from features.logistics.forms import AccommodationForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def two_offices():
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")
    return velky_meder, gyor


def test_accommodation_form_defaults_office_to_users_single_office(
    django_user_model, two_offices
):
    velky_meder, _gyor = two_offices
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    form = AccommodationForm(user=manager)
    assert list(form.fields["office"].queryset) == [velky_meder]
    assert form.fields["office"].initial == velky_meder


def test_accommodation_form_offers_all_offices_to_observer(
    django_user_model, two_offices
):
    velky_meder, gyor = two_offices
    observer = django_user_model.objects.create_user(
        email="o@demo.jober.test", password="x", role="observer"
    )
    form = AccommodationForm(user=observer)
    assert set(form.fields["office"].queryset) == {velky_meder, gyor}


def test_accommodation_form_drops_the_office_field_when_no_offices_exist(
    django_user_model,
):
    """CorvinumEU: no Office rows anywhere - the field is removed entirely.

    It used to stay present and offer nothing, which asked the office to
    choose from an empty list (changed 2026-08-04). The form still validates
    without it, and the switch is keyed on the data, not the client."""
    manager = django_user_model.objects.create_user(
        email="m@demo.corvinum.test", password="x", role="manager"
    )
    form = AccommodationForm(
        data={"name": "Test House", "address": "", "notes": "", "is_active": True},
        user=manager,
    )
    assert "office" not in form.fields
    assert form.is_valid(), form.errors
