"""Advance & deduction ledger services (Stage C2, ADR 0022; design doc §5.10).

Money rules built to the recorded C-Q2..C-Q5 defaults (corvinum-open-questions):
Europe/Bratislava, Thursday **14:00** cut-off with late entries rolling to the
next week, the 20th-to-20th cycle keyed by its end month (21st → 20th
inclusive), no hard deletes, reversal-only corrections after cycle inclusion,
full advance recovery in a single cycle (no partial recovery in MVP).
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext as _

from core.audit.services import record_event
from features.advances.models import (
    TYPE_PAY_EFFECTS,
    EntryType,
    LedgerEntry,
    PayEffect,
    SettlementStatus,
)

THURSDAY = 3  # date.weekday()
CUTOFF = dt.time(14, 0)  # C-Q2 proposed default, pending client confirmation


class LedgerError(Exception):
    """A ledger rule was violated."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LedgerError(message)


@transaction.atomic
def record_entry(
    person,
    *,
    entry_type: str,
    category: str,
    amount: Decimal,
    actor=None,
    project=None,
    pay_effect: str = "",
    note: str = "",
    entry_date: dt.date | None = None,
    reversal_of: LedgerEntry | None = None,
) -> LedgerEntry:
    amount = Decimal(amount)
    _require(amount > 0, _("Amount must be positive — meaning lives in the entry type."))
    expected = TYPE_PAY_EFFECTS[EntryType(entry_type)]
    effect = pay_effect or expected
    _require(
        effect in (expected, PayEffect.NONE),
        _("%(t)s entries carry pay effect %(e)s (or none).") % {"t": entry_type, "e": expected},
    )
    entry = LedgerEntry.objects.create(
        person=person,
        project=project,
        entry_type=entry_type,
        category=category,
        amount=amount,
        pay_effect=effect,
        entry_date=entry_date or timezone.localdate(),
        note=note,
        reversal_of=reversal_of,
        created_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    record_event(
        actor, "ledger.entry_recorded", target=person,
        reason=f"{entry_type} {category} {amount} EUR",
        entry_id=entry.pk,
    )
    return entry


@transaction.atomic
def cancel_entry(entry: LedgerEntry, *, actor=None, reason: str = "") -> LedgerEntry:
    """CANCELLED is only for entries never acted on (C-Q5)."""
    _require(
        entry.settlement_status == SettlementStatus.OPEN,
        _("Only open entries can be cancelled; settled entries need a reversal."),
    )
    entry.settlement_status = SettlementStatus.CANCELLED
    entry.save(update_fields=["settlement_status"])
    record_event(actor, "ledger.entry_cancelled", target=entry.person, reason=reason, entry_id=entry.pk)
    return entry


@transaction.atomic
def reverse_entry(entry: LedgerEntry, *, actor=None, reason: str = "") -> LedgerEntry:
    """Correction path for locked entries: a new entry with the opposite pay
    effect, linked to the original (C-Q5). The original stays untouched."""
    _require(entry.is_locked, _("Open entries are cancelled, not reversed."))
    _require(not hasattr(entry, "reversed_by"), _("Entry is already reversed."))
    opposite = {
        PayEffect.DEDUCT: EntryType.PAY_ADDITION,
        PayEffect.ADD: EntryType.PAY_DEDUCTION,
    }
    _require(entry.pay_effect in opposite, _("Entries without payroll effect cannot be reversed."))
    reversal = record_entry(
        entry.person,
        entry_type=opposite[entry.pay_effect],
        category=entry.category,
        amount=entry.amount,
        actor=actor,
        project=entry.project,
        note=reason or f"reversal of #{entry.pk}",
        reversal_of=entry,
    )
    record_event(actor, "ledger.entry_reversed", target=entry.person, reason=reason, entry_id=entry.pk)
    return reversal


# --- Thursday weekly summary (C-Q2) -----------------------------------------

def week_cutoff(on: dt.date) -> dt.datetime:
    """The Thursday-14:00 cut-off of the week containing ``on`` (local time)."""
    thursday = on + dt.timedelta(days=THURSDAY - on.weekday())
    naive = dt.datetime.combine(thursday, CUTOFF)
    return timezone.make_aware(naive)


def thursday_summary(on: dt.date):
    """Open cash advances belonging to this week's Friday distribution:
    created after last week's cut-off, up to this week's cut-off. Entries
    after the cut-off roll to next week — never retro-inserted (C-Q2)."""
    cutoff = week_cutoff(on)
    previous = cutoff - dt.timedelta(days=7)
    entries = (
        LedgerEntry.objects.filter(
            entry_type=EntryType.CASH_ADVANCE,
            settlement_status=SettlementStatus.OPEN,
            created_at__gt=previous,
            created_at__lte=cutoff,
        )
        .select_related("person", "project")
        .order_by("project__name", "person__last_name", "created_at")
    )
    total = entries.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return {"cutoff": cutoff, "entries": list(entries), "total": total}


# --- 20th-to-20th cycle (C-Q3) -----------------------------------------------

def cycle_bounds(year: int, month: int) -> tuple[dt.date, dt.date]:
    """Cycle keyed by end month: 21st of the previous month → 20th of
    ``month``, both inclusive; correct across December→January."""
    end = dt.date(year, month, 20)
    start = (dt.date(year, month, 1) - dt.timedelta(days=1)).replace(day=21)
    return start, end


def cycle_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def cycle_report(year: int, month: int):
    """Per-person net payroll effect for the cycle (ADD − DEDUCT, both from
    positive magnitudes), plus the raw entries."""
    start, end = cycle_bounds(year, month)
    entries = (
        LedgerEntry.objects.filter(entry_date__gte=start, entry_date__lte=end)
        .exclude(settlement_status=SettlementStatus.CANCELLED)
        .select_related("person", "project")
        .order_by("person__last_name", "entry_date")
    )
    per_person: dict = {}
    for e in entries:
        row = per_person.setdefault(
            e.person_id, {"person": e.person, "deduct": Decimal("0"), "add": Decimal("0")}
        )
        if e.pay_effect == PayEffect.DEDUCT:
            row["deduct"] += e.amount
        elif e.pay_effect == PayEffect.ADD:
            row["add"] += e.amount
    for row in per_person.values():
        row["net"] = row["add"] - row["deduct"]
    return {"start": start, "end": end, "entries": list(entries), "rows": list(per_person.values())}


@transaction.atomic
def include_cycle(year: int, month: int, *, actor=None) -> int:
    """Assign every open entry of the cycle window to the cycle and lock it
    (OPEN → INCLUDED_IN_CYCLE).

    When the wage-ledger feature is enabled, open cash advances are excluded:
    each advance settles through its manager-confirmed wage-recovery
    assignment so it always carries an explicit recovery pointer. Without the
    wage ledger, advances keep settling through bulk inclusion as before.
    """
    from core.ui.registry import flag_enabled

    start, end = cycle_bounds(year, month)
    entries = LedgerEntry.objects.select_for_update().filter(
        settlement_status=SettlementStatus.OPEN,
        entry_date__gte=start,
        entry_date__lte=end,
    )
    if flag_enabled("wage_ledger"):
        entries = entries.exclude(entry_type=EntryType.CASH_ADVANCE)
    count = 0
    for entry in entries:
        entry.settlement_status = SettlementStatus.INCLUDED_IN_CYCLE
        entry.cycle_key = cycle_key(year, month)
        entry.save(update_fields=["settlement_status", "cycle_key"])
        count += 1
    record_event(actor, "ledger.cycle_included", reason=cycle_key(year, month), count=count)
    return count


@transaction.atomic
def include_entry(entry: LedgerEntry, *, cycle_key: str, actor=None) -> LedgerEntry:
    """Lock a single open entry into a settlement cycle (OPEN →
    INCLUDED_IN_CYCLE). Generic per-entry counterpart of ``include_cycle`` for
    callers that settle entries individually rather than by window."""
    _require(
        entry.settlement_status == SettlementStatus.OPEN,
        _("Only open entries can be included in a settlement cycle."),
    )
    entry.settlement_status = SettlementStatus.INCLUDED_IN_CYCLE
    entry.cycle_key = cycle_key
    entry.save(update_fields=["settlement_status", "cycle_key"])
    record_event(
        actor, "ledger.entry_included", target=entry.person,
        reason=cycle_key, entry_id=entry.pk,
    )
    return entry


@transaction.atomic
def mark_cycle_deducted(year: int, month: int, *, actor=None) -> int:
    """INCLUDED_IN_CYCLE → DEDUCTED for the cycle (pay has been settled)."""
    key = cycle_key(year, month)
    count = LedgerEntry.objects.filter(
        settlement_status=SettlementStatus.INCLUDED_IN_CYCLE, cycle_key=key
    ).update(settlement_status=SettlementStatus.DEDUCTED)
    record_event(actor, "ledger.cycle_deducted", reason=key, count=count)
    return count


def open_balance(person) -> Decimal:
    """Net outstanding payroll effect of unsettled entries (DEDUCT − ADD):
    what the person currently owes against future pay."""
    rows = LedgerEntry.objects.filter(
        person=person,
        settlement_status__in=(SettlementStatus.OPEN, SettlementStatus.INCLUDED_IN_CYCLE),
    ).exclude(pay_effect=PayEffect.NONE)
    deduct = rows.filter(pay_effect=PayEffect.DEDUCT).aggregate(t=Sum("amount"))["t"] or Decimal("0")
    add = rows.filter(pay_effect=PayEffect.ADD).aggregate(t=Sum("amount"))["t"] or Decimal("0")
    return deduct - add


def guard_editable(entry: LedgerEntry) -> None:
    _require(not entry.is_locked, _("Entry is locked after cycle inclusion; record a reversal instead."))
