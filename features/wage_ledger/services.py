from __future__ import annotations

import datetime as dt
import re
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils.translation import gettext as _

from core.audit.services import record_event
from features.advances.models import (
    EntryType,
    LedgerEntry,
    PayEffect,
    SettlementStatus,
)
from features.advances.services import include_entry
from features.wage_ledger.models import AdvanceRecovery, WageEntry

PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@transaction.atomic
def record_wage(
    person,
    *,
    period: str,
    gross_amount,
    note: str = "",
    actor=None,
) -> WageEntry:
    try:
        amount = Decimal(str(gross_amount))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(_("Enter a valid gross amount.")) from exc

    entry = WageEntry(
        person=person,
        period=period,
        gross_amount=amount,
        note=note,
        created_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    entry.full_clean()
    try:
        entry.save()
    except IntegrityError as exc:
        raise ValidationError(
            _("A wage is already recorded for this person and period.")
        ) from exc
    record_event(
        actor,
        "wage.recorded",
        target=entry,
        person_id=person.pk,
        person=str(person),
        period=entry.period,
        gross_amount=str(entry.gross_amount),
        currency=entry.currency,
    )
    return entry


def wage_history(person):
    return person.wage_entries.select_related("created_by").order_by("-period", "-id")


# --- Advance recovery (which advance settles in which wage month) ------------

def suggested_recovery_period(entry_date: dt.date) -> str:
    """First wage month whose 21st→20th cycle window contains the advance:
    on or before the 20th of month M → M; the 21st or later → M+1 (the
    cross-cycle deferral rule, correct across December→January)."""
    year, month = entry_date.year, entry_date.month
    if entry_date.day > 20:
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return f"{year:04d}-{month:02d}"


def is_deferred(entry_date: dt.date, period: str) -> bool:
    return period != f"{entry_date.year:04d}-{entry_date.month:02d}"


@transaction.atomic
def assign_recovery(
    advance: LedgerEntry,
    *,
    period: str = "",
    amount=None,
    note: str = "",
    actor=None,
) -> AdvanceRecovery:
    """Manager-confirmed assignment of an advance to a wage month. Never
    assigns an advance to a wage month whose cycle window it postdates: the
    chosen month must be the suggested one or later."""
    if advance.entry_type != EntryType.CASH_ADVANCE:
        raise ValidationError(_("Only cash advances can be assigned a wage recovery."))
    if advance.settlement_status != SettlementStatus.OPEN:
        raise ValidationError(_("This advance is already assigned or settled."))

    suggested = suggested_recovery_period(advance.entry_date)
    period = (period or suggested).strip()
    if not PERIOD_RE.match(period):
        raise ValidationError(_("Use the YYYY-MM format."))
    if period < suggested:
        raise ValidationError(
            _("This advance falls in the cycle ending on the 20th; the earliest "
              "wage month that can recover it is %(period)s.")
            % {"period": suggested}
        )

    try:
        amount = advance.amount if amount is None else Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(_("Enter a valid recovery amount.")) from exc
    if not Decimal("0") < amount <= advance.amount:
        raise ValidationError(
            _("Recovery amount must be positive and at most the advance amount.")
        )

    recovery = AdvanceRecovery(
        advance=advance,
        recovered_in_period=period,
        amount=amount,
        note=note,
        assigned_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    recovery.full_clean()
    try:
        recovery.save()
    except IntegrityError as exc:
        raise ValidationError(
            _("This advance already has an active wage recovery.")
        ) from exc
    # Settlement lifecycle stays owned by advances: OPEN → INCLUDED_IN_CYCLE
    # through its service layer, never by touching settlement_status here.
    include_entry(advance, cycle_key=period, actor=actor)
    record_event(
        actor,
        "wage.recovery_assigned",
        target=recovery,
        person_id=advance.person_id,
        person=str(advance.person),
        advance_id=advance.pk,
        period=period,
        amount=str(amount),
        deferred=is_deferred(advance.entry_date, period),
    )
    return recovery


def pending_advances(person=None):
    """Open cash advances awaiting a recovery assignment, oldest first."""
    entries = LedgerEntry.objects.filter(
        entry_type=EntryType.CASH_ADVANCE,
        settlement_status=SettlementStatus.OPEN,
    ).select_related("person")
    if person is not None:
        entries = entries.filter(person=person)
    return entries.order_by("entry_date", "id")


def compute_net(person, period: str) -> Decimal | None:
    """Derived net for a wage month — computed at read time, never stored:
    gross − Σ(recovery amounts for the period) − Σ(other DEDUCT entries settled
    in the period) + Σ(ADD entries settled in the period). Advances with an
    active recovery contribute their recovery amount, not the entry amount, so
    nothing is counted twice and partial recovery stays representable."""
    wage = WageEntry.objects.filter(person=person, period=period).first()
    if wage is None:
        return None
    recoveries = AdvanceRecovery.objects.filter(
        advance__person=person, is_active=True
    )
    recovery_total = (
        recoveries.filter(recovered_in_period=period).aggregate(t=Sum("amount"))["t"]
        or Decimal("0")
    )
    ledger = (
        LedgerEntry.objects.filter(person=person, cycle_key=period)
        .exclude(settlement_status=SettlementStatus.CANCELLED)
        .exclude(pk__in=recoveries.values("advance_id"))
    )
    deduct = (
        ledger.filter(pay_effect=PayEffect.DEDUCT).aggregate(t=Sum("amount"))["t"]
        or Decimal("0")
    )
    add = (
        ledger.filter(pay_effect=PayEffect.ADD).aggregate(t=Sum("amount"))["t"]
        or Decimal("0")
    )
    return wage.gross_amount - recovery_total - deduct + add
