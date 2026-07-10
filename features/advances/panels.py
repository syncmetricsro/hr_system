"""Person-card contribution of the advances ledger."""

from __future__ import annotations

from core.accounts.permissions import Action
from core.accounts.permissions import can as user_can
from core.ui.registry import flag_enabled
from features.advances.models import EntryType, LedgerCategory
from features.advances.services import open_balance


def ledger_panel(request, person):
    if not flag_enabled("advances"):
        return None
    if not user_can(request.user, Action.LEDGER_VIEW):
        return None
    entries = person.ledger_entries.select_related("project")[:8]
    return {
        "ledger_entries": entries,
        "ledger_open_balance": open_balance(person),
        "can_enter_ledger": user_can(request.user, Action.LEDGER_ENTER),
        "ledger_entry_types": EntryType.choices,
        "ledger_categories": LedgerCategory.choices,
    }
