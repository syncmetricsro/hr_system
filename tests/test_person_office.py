from __future__ import annotations

import pytest

from core.offices.models import Office
from core.people.forms import PersonForm
from features.intake.models import IntakeQuestionnaireVersion, QuestionnaireStatus
from features.intake.services import complete_intake, start_intake

pytestmark = pytest.mark.django_db


@pytest.fixture
def two_offices():
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")
    return velky_meder, gyor


@pytest.fixture
def questionnaire():
    return IntakeQuestionnaireVersion.objects.create(
        name="Test intake", version=1, status=QuestionnaireStatus.PUBLISHED
    )


def test_person_form_defaults_office_to_users_single_office(
    django_user_model, two_offices
):
    velky_meder, _gyor = two_offices
    recruiter = django_user_model.objects.create_user(
        email="r@demo.jober.test", password="x", role="recruiter"
    )
    recruiter.offices.set([velky_meder])
    form = PersonForm(user=recruiter)
    assert list(form.fields["office"].queryset) == [velky_meder]
    assert form.fields["office"].initial == velky_meder


def test_person_form_offers_only_users_offices_when_multi_office(
    django_user_model, two_offices
):
    velky_meder, gyor = two_offices
    recruiter = django_user_model.objects.create_user(
        email="r@demo.jober.test", password="x", role="recruiter"
    )
    recruiter.offices.set([velky_meder, gyor])
    form = PersonForm(user=recruiter)
    assert set(form.fields["office"].queryset) == {velky_meder, gyor}
    assert form.fields["office"].initial is None


def test_person_form_offers_all_offices_to_observer(django_user_model, two_offices):
    velky_meder, gyor = two_offices
    observer = django_user_model.objects.create_user(
        email="o@demo.jober.test", password="x", role="observer"
    )
    form = PersonForm(user=observer)
    assert set(form.fields["office"].queryset) == {velky_meder, gyor}


def test_person_form_office_field_optional_and_empty_when_no_offices_exist(
    django_user_model,
):
    """CorvinumEU: no Office rows anywhere - the field stays present but
    offers nothing, and the form still validates without it."""
    manager = django_user_model.objects.create_user(
        email="m@demo.corvinum.test", password="x", role="manager"
    )
    form = PersonForm(
        data={
            "first_name": "Test",
            "last_name": "Worker",
            "email": "",
            "phone": "",
            "address": "",
            "nationality": "",
            "preferred_language": "",
            "date_of_birth": "",
            "place_of_birth": "",
            "has_disability": "",
            "disability_type": "",
        },
        user=manager,
    )
    assert list(form.fields["office"].queryset) == []
    assert form.is_valid(), form.errors


def test_complete_intake_sets_office_from_single_office_recruiter(
    django_user_model, two_offices, questionnaire
):
    velky_meder, _gyor = two_offices
    recruiter = django_user_model.objects.create_user(
        email="r@demo.jober.test", password="x", role="recruiter"
    )
    recruiter.offices.set([velky_meder])
    intake = start_intake(recruiter, questionnaire)
    person = complete_intake(intake, actor=recruiter)
    assert person.office == velky_meder


def test_complete_intake_leaves_office_unset_for_multi_office_recruiter(
    django_user_model, two_offices, questionnaire
):
    velky_meder, gyor = two_offices
    recruiter = django_user_model.objects.create_user(
        email="r@demo.jober.test", password="x", role="recruiter"
    )
    recruiter.offices.set([velky_meder, gyor])
    intake = start_intake(recruiter, questionnaire)
    person = complete_intake(intake, actor=recruiter)
    assert person.office is None
