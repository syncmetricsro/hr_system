from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from django.core.exceptions import PermissionDenied

from core.accounts.permissions import Action, require_action, user_office_scope
from core.offices.scoping import assert_person_in_scope
from features.intake.models import RecruitmentIntake
from features.intake.services import (
    answers_map,
    current_panel,
    ordered_panels,
    published_questionnaire,
    save_panel,
    start_intake,
)


@require_action(Action.INTAKE_CREATE_EDIT)
def intake_start(request: HttpRequest) -> HttpResponse:
    questionnaire = published_questionnaire()
    if questionnaire is None:
        messages.error(request, _("No published intake questionnaire."))
        return redirect("people_list")
    intake = start_intake(request.user, questionnaire)
    return redirect("intake_panel", pk=intake.pk)


def _assert_intake_in_scope(user, intake: RecruitmentIntake) -> None:
    """An intake carries no office of its own (ADR 0026).

    Before completion it belongs to the recruiter running it; afterwards a
    Person exists and that person's office governs. This mirrors the
    office-less-Person rule - fall back to ownership rather than making the
    record either universally visible or invisible to its own author. It is
    deliberately strict: a colleague in the same office cannot open a
    half-finished intake. Widen it if that proves annoying in practice, but
    widen it on purpose.
    """
    if user_office_scope(user) is None:
        return
    if intake.person_id is not None:
        assert_person_in_scope(user, intake.person)
        return
    if intake.recruiter_id != getattr(user, "pk", None):
        raise PermissionDenied("This intake belongs to another recruiter.")


@require_action(Action.INTAKE_CREATE_EDIT)
def intake_panel(request: HttpRequest, pk: int) -> HttpResponse:
    intake = get_object_or_404(RecruitmentIntake, pk=pk)
    _assert_intake_in_scope(request.user, intake)
    if intake.status == RecruitmentIntake.Status.COMPLETED and intake.person_id:
        return redirect("person_detail", pk=intake.person_id)

    panel = current_panel(intake)
    errors: dict[str, str] = {}
    if request.method == "POST" and panel is not None:
        raw_errors = save_panel(
            intake, request.POST, actor=request.user, http_request=request
        )
        if not raw_errors:
            if intake.status == RecruitmentIntake.Status.COMPLETED and intake.person_id:
                messages.success(request, _("Intake complete — person added."))
                return redirect("person_detail", pk=intake.person_id)
            return redirect("intake_panel", pk=intake.pk)
        errors = {
            key: (
                _("Please type a value (or the word for 'none').")
                if code == "type_required"
                else _("Enter a valid email address.")
                if code == "invalid_email"
                else _("Required.")
            )
            for key, code in raw_errors.items()
        }
        panel = current_panel(intake)

    existing = answers_map(intake)
    panels = ordered_panels(intake)
    questions = []
    for q in panel.questions.all():
        answer = existing.get(q.stable_key)
        questions.append(
            {
                "q": q,
                "value": answer.value if answer else "",
                "error": errors.get(q.stable_key, ""),
            }
        )
    return TemplateResponse(
        request,
        "pages/intake_panel.html",
        {
            "intake": intake,
            "panel": panel,
            "questions": questions,
            "step": intake.current_panel_order + 1,
            "total": len(panels),
        },
    )
