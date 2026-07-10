"""Person-card contribution of the checklists feature."""

from __future__ import annotations

from core.accounts.permissions import Action
from core.accounts.permissions import can as user_can
from core.ui.registry import flag_enabled
from features.checklists.services import ensure_person_checklist


def checklist_panel(request, person):
    if not flag_enabled("checklists"):
        return None
    items = ensure_person_checklist(person)
    if not items:
        return None
    return {
        "checklist_items": items,
        "can_tick_checklist": user_can(request.user, Action.CHECKLIST_TICK),
        "checklist_missing_critical": sum(
            1 for i in items if i.item_template.critical and not i.done
        ),
    }
