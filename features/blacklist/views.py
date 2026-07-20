from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action
from features.blacklist.models import BlacklistCase, BlacklistCaseStatus, BlacklistCategory
from features.blacklist.services import (
    BlacklistError,
    compute_composite_identifier,
    decide_case,
    propose_case,
    remove_case,
)
from core.people.models import Person


@require_action(Action.BLACKLIST_DECIDE)
def blacklist_queue(request: HttpRequest) -> TemplateResponse:
    """Manager review queue: proposed cases awaiting a decision (plan §12.13)."""
    cases = (
        BlacklistCase.objects.filter(status=BlacklistCaseStatus.PROPOSED)
        .select_related("person", "category", "proposed_by")
        .prefetch_related("fingerprints")
    )
    return TemplateResponse(request, "pages/blacklist_queue.html", {"cases": cases})


@require_POST
@require_action(Action.BLACKLIST_PROPOSE)
def blacklist_propose(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    category = BlacklistCategory.objects.filter(
        pk=request.POST.get("category"), is_active=True
    ).first()
    maiden = request.POST.get("mothers_maiden_name", "")
    composite = compute_composite_identifier(
        person.first_name, person.last_name, person.date_of_birth, maiden
    ) if maiden else None
    propose_case(
        person, category=category, reason=request.POST.get("reason", ""),
        identifier=request.POST.get("identifier") or None,
        identifier_type=request.POST.get("identifier_type", "national_id"),
        composite_identifier=composite,
        actor=request.user,
    )
    messages.success(request, _("Blacklist case proposed for review."))
    return redirect("person_detail", pk=person.pk)


@require_POST
@require_action(Action.BLACKLIST_DECIDE)
def blacklist_decide(request: HttpRequest, pk: int) -> HttpResponse:
    case = get_object_or_404(BlacklistCase, pk=pk)
    try:
        decide_case(case, request.POST.get("decision"), actor=request.user,
                    reason=request.POST.get("reason", ""))
        messages.success(request, _("Decision recorded."))
    except BlacklistError as exc:
        messages.error(request, str(exc))
    return redirect("blacklist_queue")


@require_POST
@require_action(Action.BLACKLIST_DECIDE)
def blacklist_remove(request: HttpRequest, pk: int) -> HttpResponse:
    case = get_object_or_404(BlacklistCase, pk=pk)
    try:
        remove_case(case, actor=request.user, reason=request.POST.get("reason", ""))
        messages.success(request, _("Removed from blacklist."))
    except BlacklistError as exc:
        messages.error(request, str(exc))
    return redirect("person_detail", pk=case.person_id)
