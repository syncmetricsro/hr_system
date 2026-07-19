from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, can, require_action
from features.advances.models import LedgerEntry
from features.wage_ledger.forms import WageEntryForm
from features.wage_ledger.models import AdvanceRecovery, WageEntry
from features.wage_ledger.services import (
    assign_recovery,
    is_deferred,
    pending_advances,
    record_wage,
    suggested_recovery_period,
)


def _page_context(request, *, form=None) -> dict:
    may_manage = can(request.user, Action.WAGE_MANAGE)
    pending = []
    for entry in pending_advances()[:100]:
        suggested = suggested_recovery_period(entry.entry_date)
        pending.append({
            "entry": entry,
            "suggested": suggested,
            "deferred": is_deferred(entry.entry_date, suggested),
        })
    return {
        "wages": WageEntry.objects.select_related("person", "created_by")[:100],
        "may_manage": may_manage,
        "form": form if form is not None else (WageEntryForm() if may_manage else None),
        "pending_advances": pending,
        "recoveries": AdvanceRecovery.objects.filter(is_active=True).select_related(
            "advance__person", "assigned_by"
        )[:100],
    }


@require_action(Action.WAGE_VIEW)
def wage_list(request):
    return render(request, "pages/wages.html", _page_context(request))


@require_POST
@require_action(Action.WAGE_MANAGE)
def wage_record(request):
    form = WageEntryForm(request.POST)
    if form.is_valid():
        try:
            record_wage(
                form.cleaned_data["person"],
                period=form.cleaned_data["period"],
                gross_amount=form.cleaned_data["gross_amount"],
                note=form.cleaned_data["note"],
                actor=request.user,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, _("Gross wage recorded."))
            return redirect("wage_list")
    return render(
        request,
        "pages/wages.html",
        _page_context(request, form=form),
        status=400,
    )


@require_POST
@require_action(Action.WAGE_MANAGE)
def wage_recovery_assign(request):
    advance = get_object_or_404(LedgerEntry, pk=request.POST.get("advance"))
    try:
        assign_recovery(
            advance,
            period=request.POST.get("period", "").strip(),
            note=request.POST.get("note", "").strip(),
            actor=request.user,
        )
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    else:
        messages.success(request, _("Advance recovery assigned."))
    return redirect("wage_list")
