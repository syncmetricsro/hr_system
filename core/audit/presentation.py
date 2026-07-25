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
    "accommodation.cost_period_set": _("Accommodation cost period saved"),
    "accommodation.created": _("Accommodation created"),
    "accommodation.rate_set": _("Room rate saved"),
    "accommodation.updated": _("Accommodation updated"),
    "accommodation.worker_payment_set": _("Worker accommodation payment saved"),
    "assignment.created": _("Assigned to project"),
    "assignment.ended": _("Project assignment ended"),
    "auth.login": _("Signed in"),
    "auth.logout": _("Signed out"),
    "auth.totp_enabled": _("Two-factor authentication enabled"),
    "auth.totp_failed": _("Two-factor authentication failed"),
    "blacklist.decided": _("Blacklist decision recorded"),
    "blacklist.proposed": _("Blacklist case proposed"),
    "blacklist.removed": _("Removed from blacklist"),
    "certificate.deleted": _("Certificate deleted"),
    "certificate.replaced": _("Certificate document replaced"),
    "certificate.updated": _("Certificate updated"),
    "certificate.uploaded": _("Certificate uploaded"),
    "checklist.item_ticked": _("Checklist item completed"),
    "checklist.item_unticked": _("Checklist item reopened"),
    "equipment.catalog_created": _("Equipment item created"),
    "equipment.catalog_updated": _("Equipment item updated"),
    "equipment.deduction_reviewed": _("Equipment deduction review recorded"),
    "equipment.flagged_unreturned": _("Equipment flagged as unreturned"),
    "equipment.issued": _("Equipment issued"),
    "equipment.returned": _("Equipment returned"),
    "equipment.stock_adjusted": _("Equipment stock adjusted"),
    "equipment.stock_received": _("Equipment stock received"),
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
    "person.avatar_added": _("Avatar added"),
    "person.avatar_removed": _("Avatar removed"),
    "person.avatar_replaced": _("Avatar replaced"),
    "person.created": _("Person added"),
    "person.exited": _("Exit completed"),
    "person.lifecycle_changed": _("Status changed"),
    "person.recycled": _("Recycled to Available"),
    "person.updated": _("Person updated"),
    "readiness.updated": _("Readiness saved"),
    "room.assigned": _("Room assigned"),
    "room.created": _("Room created"),
    "room.released": _("Room released"),
    "room.updated": _("Room updated"),
    "sms.sent": _("Message sent"),
    "transport.week_created": _("Transport week created"),
    "transport.week_recorded": _("Transport week recorded"),
    "transport.week_updated": _("Transport week updated"),
    "trial.outcome_recorded": _("Trial outcome recorded"),
    "trial.scheduled": _("Trial scheduled"),
    "trial.updated": _("Trial updated"),
    "user.avatar_added": _("Avatar added"),
    "user.avatar_removed": _("Avatar removed"),
    "user.avatar_replaced": _("Avatar replaced"),
    "wage.recorded": _("Gross wage recorded"),
}


def audit_action_label(action: str) -> str:
    """Translate a known action code, with a readable fallback for old data."""
    if action in AUDIT_ACTION_LABELS:
        return str(AUDIT_ACTION_LABELS[action])
    return action.replace(".", " — ").replace("_", " ").capitalize()


# AuditEvent.reason is mostly free text (user-typed or interpolated), but a
# handful of call sites pass one of these fixed English literals as a
# default.  Those are genuinely translatable finite vocabulary; anything else
# passes through unchanged, exactly like reason has always behaved.
AUDIT_REASON_LABELS = {
    "activation": _("Activated onto a project"),
    "blacklist removed": _("Removed from blacklist"),
    "blacklisted": _("Added to blacklist"),
    "exit": _("Exit"),
    "readiness met": _("Readiness requirements met"),
    "reassigned": _("Room reassigned"),
    "recycled": _("Recycled to Available"),
    "superseded": _("Superseded by a new assignment"),
    "trial fail": _("Trial failed"),
    "trial no_show": _("Trial no-show"),
    "trial scheduled": _("Trial scheduled"),
}


def audit_reason_label(reason: str) -> str:
    """Translate a reason string if it matches a known fixed literal.

    Most reasons are free text with no fixed vocabulary, so unmatched values
    are returned unchanged rather than mangled into a readable fallback.
    """
    if reason in AUDIT_REASON_LABELS:
        return str(AUDIT_REASON_LABELS[reason])
    return reason
