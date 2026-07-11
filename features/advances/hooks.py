"""Cross-feature contribution: approved equipment charges become linked
PAY_DEDUCTION ledger entries (design doc §5.8 ↔ §5.10). Registered only when
the logistics feature is installed; no-ops unless the ``advances`` flag is on."""

from __future__ import annotations

from decimal import Decimal

from django.utils.translation import gettext as _

from core.ui.registry import flag_enabled
from features.advances.models import EntryType, LedgerCategory
from features.advances.services import record_entry


def equipment_charge_to_ledger(issue, *, actor=None) -> None:
    if not flag_enabled("advances"):
        return
    amount = issue.charge_amount or Decimal("0")
    if amount <= 0:
        return
    project = None
    active = issue.person.assignments.filter(status="active").select_related("project").first()
    if active:
        project = active.project
    record_entry(
        issue.person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount=amount,
        actor=actor,
        project=project,
        note=_("equipment charge: %(item)s ×%(qty)s (issue #%(id)s)") % {"item": _(issue.item.name), "qty": issue.quantity, "id": issue.pk},
    )
