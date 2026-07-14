"""Localized, human-readable labels for immutable audit action codes.

AuditEvent.action intentionally stores a stable machine code.  This mapping is
the presentation boundary: it never changes persisted event data or filtering.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _


AUDIT_ACTION_LABELS = {
    "accounts.superuser_created": _("Administrator account created"),
    "accounts.superuser_ensured": _("Administrator account updated"),
    "accommodation.assignment_rate_set": _("Accommodation rate override saved"),
    "accommodation.rate_set": _("Room rate saved"),
    "assignment.created": _("Assigned to project"),
    "assignment.ended": _("Project assignment ended"),
    "auth.login": _("Signed in"),
    "auth.logout": _("Signed out"),
    "auth.totp_enabled": _("Two-factor authentication enabled"),
    "auth.totp_failed": _("Two-factor authentication failed"),
    "blacklist.decided": _("Blacklist decision recorded"),
    "blacklist.proposed": _("Blacklist case proposed"),
    "blacklist.removed": _("Removed from blacklist"),
    "checklist.item_ticked": _("Checklist item completed"),
    "checklist.item_unticked": _("Checklist item reopened"),
    "equipment.deduction_reviewed": _("Equipment deduction review recorded"),
    "equipment.flagged_unreturned": _("Equipment flagged as unreturned"),
    "equipment.issued": _("Equipment issued"),
    "equipment.returned": _("Equipment returned"),
    "finance.line_item_set": _("Finance line item saved"),
    "finance.locked": _("Financial month locked"),
    "finance.month_recorded": _("Financial month recorded"),
    "finance.recomputed": _("Finance recalculated"),
    "finance.reopened": _("Financial month reopened"),
    "feedback.received": _("Worker feedback received"),
    "intake.completed": _("Intake completed"),
    "ledger.cycle_deducted": _("Ledger cycle marked settled"),
    "ledger.cycle_included": _("Ledger entries included in cycle"),
    "ledger.entry_cancelled": _("Ledger entry cancelled"),
    "ledger.entry_recorded": _("Ledger entry recorded"),
    "ledger.entry_reversed": _("Ledger entry reversed"),
    "payslip.recorded": _("Payslip recorded"),
    "payslip.sent": _("Payslip sent"),
    "person.archived": _("Person archived"),
    "person.created": _("Person added"),
    "person.exited": _("Exit completed"),
    "person.lifecycle_changed": _("Status changed"),
    "person.recycled": _("Recycled to Available"),
    "person.updated": _("Person updated"),
    "readiness.updated": _("Readiness saved"),
    "room.assigned": _("Room assigned"),
    "room.released": _("Room released"),
    "sms.sent": _("Message sent"),
    "transport.week_recorded": _("Transport week recorded"),
    "trial.outcome_recorded": _("Trial outcome recorded"),
    "trial.scheduled": _("Trial scheduled"),
}


def audit_action_label(action: str) -> str:
    """Translate a known action code, with a readable fallback for old data."""
    if action in AUDIT_ACTION_LABELS:
        return str(AUDIT_ACTION_LABELS[action])
    return action.replace(".", " — ").replace("_", " ").capitalize()
