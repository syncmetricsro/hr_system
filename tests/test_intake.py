from __future__ import annotations

import pytest

from features.intake.models import (
    IntakePanel,
    IntakeQuestion,
    IntakeQuestionnaireVersion,
    QuestionnaireStatus,
    QuestionType,
    RecruitmentIntake,
)
from features.intake.services import save_panel, start_intake
from core.people.models import LifecycleStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def questionnaire():
    v = IntakeQuestionnaireVersion.objects.create(
        name="Test intake", version=1, status=QuestionnaireStatus.PUBLISHED
    )
    identity = IntakePanel.objects.create(questionnaire=v, title="Identity", order=0)
    compliance = IntakePanel.objects.create(questionnaire=v, title="Compliance", order=1)
    IntakeQuestion.objects.create(panel=identity, stable_key="first_name", label="First", type=QuestionType.TEXT, required=True, order=0)
    IntakeQuestion.objects.create(panel=identity, stable_key="last_name", label="Last", type=QuestionType.TEXT, required=True, order=1)
    IntakeQuestion.objects.create(
        panel=compliance, stable_key="disability", label="Disability", type=QuestionType.TEXT,
        required=True, order=0, requires_typed_negative=True, accepted_negatives=["nie", "none"],
    )
    IntakeQuestion.objects.create(
        panel=compliance, stable_key="disability_type", label="Type", type=QuestionType.TEXT,
        required=True, order=1, conditional_on="disability",
    )
    return v


@pytest.fixture
def recruiter(django_user_model):
    return django_user_model.objects.create_user(email="r@demo.jober.test", password="x", role="recruiter")


def test_required_blocks_advance(questionnaire, recruiter):
    intake = start_intake(recruiter, questionnaire)
    errors = save_panel(intake, {"first_name": "", "last_name": ""}, actor=recruiter)
    assert "first_name" in errors
    intake.refresh_from_db()
    assert intake.current_panel_order == 0  # did not advance


def test_typed_negative_cannot_be_blank(questionnaire, recruiter):
    intake = start_intake(recruiter, questionnaire)
    save_panel(intake, {"first_name": "Olha", "last_name": "K"}, actor=recruiter)
    # On the compliance panel, leaving the typed-negative blank is rejected.
    errors = save_panel(intake, {"disability": ""}, actor=recruiter)
    assert errors.get("disability") == "type_required"


def test_typed_negative_accepts_none_word_and_skips_conditional(questionnaire, recruiter):
    intake = start_intake(recruiter, questionnaire)
    save_panel(intake, {"first_name": "Olha", "last_name": "K"}, actor=recruiter)
    # "nie" is an accepted negative -> disability_type (conditional) not required.
    errors = save_panel(intake, {"disability": "nie"}, actor=recruiter)
    assert errors == {}
    intake.refresh_from_db()
    assert intake.status == RecruitmentIntake.Status.COMPLETED
    person = intake.person
    assert person.has_disability is False


def test_positive_disability_requires_type(questionnaire, recruiter):
    intake = start_intake(recruiter, questionnaire)
    save_panel(intake, {"first_name": "Olha", "last_name": "K"}, actor=recruiter)
    errors = save_panel(intake, {"disability": "reduced mobility", "disability_type": ""}, actor=recruiter)
    assert "disability_type" in errors


def test_full_completion_creates_available_person(questionnaire, recruiter):
    intake = start_intake(recruiter, questionnaire)
    save_panel(intake, {"first_name": "Olha", "last_name": "Kovalenko"}, actor=recruiter)
    save_panel(intake, {"disability": "reduced mobility", "disability_type": "mobility"}, actor=recruiter)
    intake.refresh_from_db()
    assert intake.status == RecruitmentIntake.Status.COMPLETED
    person = intake.person
    assert person.first_name == "Olha" and person.last_name == "Kovalenko"
    assert person.lifecycle_status == LifecycleStatus.AVAILABLE
    assert person.owning_recruiter == recruiter
    assert person.has_disability is True
    assert person.disability_type == "mobility"


def test_completed_intake_rejects_further_panels(questionnaire, recruiter):
    from features.intake.services import IntakeError

    intake = start_intake(recruiter, questionnaire)
    save_panel(intake, {"first_name": "A", "last_name": "B"}, actor=recruiter)
    save_panel(intake, {"disability": "none"}, actor=recruiter)
    with pytest.raises(IntakeError):
        save_panel(intake, {"x": "y"}, actor=recruiter)
