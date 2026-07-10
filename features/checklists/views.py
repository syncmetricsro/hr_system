from __future__ import annotations

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action
from features.checklists.models import PersonChecklistItem
from features.checklists.services import set_item_state


@require_POST
@require_action(Action.CHECKLIST_TICK)
def toggle_item_view(request, item_pk: int):
    item = get_object_or_404(
        PersonChecklistItem.objects.select_related("person", "item_template"), pk=item_pk
    )
    set_item_state(
        item,
        done=not item.done,
        actor=request.user,
        note=request.POST.get("note", "").strip(),
    )
    return redirect("person_detail", pk=item.person_id)
