from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, require_action
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


@require_action(Action.INTAKE_CREATE_EDIT)
def intake_panel(request: HttpRequest, pk: int) -> HttpResponse:
    intake = get_object_or_404(RecruitmentIntake, pk=pk)
    if intake.status == RecruitmentIntake.Status.COMPLETED and intake.person_id:
        return redirect("person_detail", pk=intake.person_id)

    panel = current_panel(intake)
    errors: dict[str, str] = {}
    if request.method == "POST" and panel is not None:
        raw_errors = save_panel(intake, request.POST, actor=request.user)
        if not raw_errors:
            if intake.status == RecruitmentIntake.Status.COMPLETED and intake.person_id:
                messages.success(request, _("Intake complete — person added."))
                return redirect("person_detail", pk=intake.person_id)
            return redirect("intake_panel", pk=intake.pk)
        errors = {
            key: _("Please type a value (or the word for 'none').") if code == "type_required" else _("Required.")
            for key, code in raw_errors.items()
        }
        panel = current_panel(intake)

    existing = answers_map(intake)
    panels = ordered_panels(intake)
    questions = []
    for q in panel.questions.all():
        answer = existing.get(q.stable_key)
        questions.append({
            "q": q,
            "value": answer.value if answer else "",
            "error": errors.get(q.stable_key, ""),
        })
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
