from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, can, require_action
from features.wage_ledger.forms import WageEntryForm
from features.wage_ledger.models import WageEntry
from features.wage_ledger.services import record_wage


def _page_context(request, *, form=None) -> dict:
    may_manage = can(request.user, Action.WAGE_MANAGE)
    return {
        "wages": WageEntry.objects.select_related("person", "created_by")[:100],
        "may_manage": may_manage,
        "form": form if form is not None else (WageEntryForm() if may_manage else None),
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
