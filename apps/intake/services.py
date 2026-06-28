from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from apps.audit.services import record_event
from apps.intake.models import (
    IntakeAnswer,
    IntakeQuestionnaireVersion,
    QuestionnaireStatus,
    RecruitmentIntake,
)
from apps.people.models import LifecycleStatus, Person

# Marks an answer that was a typed "no/none" (not a bypassed/blank field).
NEGATIVE = "__negative__"

# stable_keys mapped straight onto Person on completion.
_DIRECT_FIELDS = (
    "first_name", "last_name", "phone", "address", "nationality",
    "preferred_language", "place_of_birth",
)


class IntakeError(Exception):
    """Raised on an invalid intake step."""


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def published_questionnaire():
    return (
        IntakeQuestionnaireVersion.objects.filter(status=QuestionnaireStatus.PUBLISHED)
        .order_by("-version")
        .prefetch_related("panels__questions")
        .first()
    )


def ordered_panels(intake):
    return list(intake.questionnaire.panels.all())


def current_panel(intake):
    panels = ordered_panels(intake)
    if 0 <= intake.current_panel_order < len(panels):
        return panels[intake.current_panel_order]
    return None


def answers_map(intake):
    return {a.question.stable_key: a for a in intake.answers.select_related("question")}


@transaction.atomic
def start_intake(recruiter, questionnaire) -> RecruitmentIntake:
    return RecruitmentIntake.objects.create(
        questionnaire=questionnaire,
        recruiter=recruiter if getattr(recruiter, "is_authenticated", False) else None,
        current_panel_order=0,
    )


def _is_positive_existing(answer) -> bool:
    return bool(answer and answer.value.strip() and answer.normalized_value != NEGATIVE)


def _parent_positive(key, parsed, existing) -> bool:
    if key in parsed:
        value, _norm, negative = parsed[key]
        return bool(value) and not negative
    return _is_positive_existing(existing.get(key))


@transaction.atomic
def save_panel(intake, post, *, actor=None) -> dict:
    """Validate + persist the current panel. Returns {} on success (and advances),
    or {stable_key: error} without advancing. Server state drives which panel is
    active, so panels cannot be bypassed by a forged POST (§12.1)."""
    panel = current_panel(intake)
    if panel is None:
        raise IntakeError("Intake is already complete.")

    questions = list(panel.questions.all())
    existing = answers_map(intake)

    # Pass 1: parse raw values + detect typed-negatives.
    parsed: dict[str, tuple[str, str, bool]] = {}
    for q in questions:
        value = (post.get(q.stable_key) or "").strip()
        negative = False
        normalized = _normalize(value)
        if q.requires_typed_negative and value:
            accepted = {_normalize(n) for n in (q.accepted_negatives or [])}
            if normalized in accepted:
                negative = True
                normalized = NEGATIVE
        parsed[q.stable_key] = (value, normalized, negative)

    # Pass 2: applicability + validation.
    errors: dict[str, str] = {}
    for q in questions:
        if q.conditional_on and not _parent_positive(q.conditional_on, parsed, existing):
            continue  # not applicable -> skip
        value, _normalized, _negative = parsed[q.stable_key]
        if q.requires_typed_negative and not value:
            errors[q.stable_key] = "type_required"
        elif q.required and not value:
            errors[q.stable_key] = "required"
    if errors:
        return errors

    # Persist applicable answers.
    for q in questions:
        applicable = not (q.conditional_on and not _parent_positive(q.conditional_on, parsed, existing))
        if not applicable:
            continue
        value, normalized, _negative = parsed[q.stable_key]
        IntakeAnswer.objects.update_or_create(
            intake=intake,
            question=q,
            defaults={
                "value": value,
                "normalized_value": normalized,
                "answered_by": actor if getattr(actor, "is_authenticated", False) else None,
            },
        )

    intake.current_panel_order += 1
    intake.save(update_fields=["current_panel_order"])

    if current_panel(intake) is None:
        complete_intake(intake, actor=actor)
    return {}


@transaction.atomic
def complete_intake(intake, *, actor=None) -> Person:
    amap = answers_map(intake)

    def val(key: str) -> str:
        answer = amap.get(key)
        return answer.value.strip() if answer else ""

    def positive(key: str) -> bool:
        return _is_positive_existing(amap.get(key))

    person = Person(
        owning_recruiter=intake.recruiter,
        lifecycle_status=LifecycleStatus.AVAILABLE,
        has_disability=positive("disability"),
        disability_type=val("disability_type"),
        date_of_birth=parse_date(val("date_of_birth")) or None,
    )
    for field in _DIRECT_FIELDS:
        setattr(person, field, val(field))
    person.save()

    intake.person = person
    intake.status = RecruitmentIntake.Status.COMPLETED
    intake.completed_at = timezone.now()
    intake.save(update_fields=["person", "status", "completed_at"])
    record_event(actor, "intake.completed", target=intake, person_id=person.pk)
    return person
