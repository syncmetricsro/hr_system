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
from django.db.models import Q, Sum
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
    _require(
        amount > 0, _("Amount must be positive — meaning lives in the entry type.")
    )
    expected = TYPE_PAY_EFFECTS[EntryType(entry_type)]
    effect = pay_effect or expected
    _require(
        effect in (expected, PayEffect.NONE),
        _("%(t)s entries carry pay effect %(e)s (or none).")
        % {"t": entry_type, "e": expected},
    )
    on = entry_date or timezone.localdate()
    entry = LedgerEntry.objects.create(
        person=person,
        project=project,
        entry_type=entry_type,
        category=category,
        amount=amount,
        pay_effect=effect,
        entry_date=on,
        note=note,
        reversal_of=reversal_of,
        created_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    record_event(
        actor,
        "ledger.entry_recorded",
        target=person,
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
    record_event(
        actor,
        "ledger.entry_cancelled",
        target=entry.person,
        reason=reason,
        entry_id=entry.pk,
    )
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
    _require(
        entry.pay_effect in opposite,
        _("Entries without payroll effect cannot be reversed."),
    )
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
    record_event(
        actor,
        "ledger.entry_reversed",
        target=entry.person,
        reason=reason,
        entry_id=entry.pk,
    )
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


def cycle_for(day: dt.date) -> tuple[int, int]:
    """The cycle a date belongs to, keyed by its end month (C-Q3).

    Days 1-20 settle in their own month; 21 onwards roll into the next one.
    """
    if day.day <= 20:
        return day.year, day.month
    return (day.year + 1, 1) if day.month == 12 else (day.year, day.month + 1)


def cycle_key_is_settled(year: int, month: int) -> bool:
    """Has this run already been closed - included in a cycle, or paid out?"""
    return LedgerEntry.objects.filter(
        cycle_key=cycle_key(year, month),
        settlement_status__in=(
            SettlementStatus.INCLUDED_IN_CYCLE,
            SettlementStatus.DEDUCTED,
        ),
    ).exists()


def cycle_is_settled(day: dt.date) -> bool:
    """Has the run covering ``day`` already been closed?

    Used to work out which run will collect a still-open entry, not to refuse
    anything: an entry landing in a closed window is carried forward (ADR 0032).
    """
    return cycle_key_is_settled(*cycle_for(day))


def settling_cycle_key(entry) -> str:
    """The run that collects this entry: the one it went into, or the next one.

    An entry already assigned to a cycle reports under that cycle for ever —
    that is history. A still-open entry reports under the next run that has not
    been closed yet, which under carry-forward is the run that will actually
    take it (ADR 0032). Walking forward matters: an advance dated 25 July whose
    August run has already gone out is collected in September, and saying "July"
    would describe a payslip that has already been paid.
    """
    if entry.cycle_key:
        return entry.cycle_key
    year, month = cycle_for(entry.entry_date)
    # Bounded so an odd data state cannot spin. Two years is far past anything
    # an office would leave outstanding.
    for _attempt in range(24):
        if not cycle_key_is_settled(year, month):
            break
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return cycle_key(year, month)


def cycle_report(year: int, month: int):
    """Per-person net payroll effect for one run (ADD − DEDUCT), plus its entries.

    What a run *did* and what a run *will do* are different questions, and this
    answers whichever applies:

    * entries already carrying this cycle key are what the run collected — a
      closed cycle keeps reporting exactly that, however the rules change later;
    * while the cycle has not been run yet, every still-open entry dated on or
      before its cutoff is added, because that is what it is about to collect
      (ADR 0032) — including strays carried forward from earlier windows.
    """
    start, end = cycle_bounds(year, month)
    key = cycle_key(year, month)
    collected = Q(cycle_key=key)
    if not LedgerEntry.objects.filter(cycle_key=key).exists():
        # Not run yet: show what it would take with it.
        collected = collected | Q(
            settlement_status=SettlementStatus.OPEN, entry_date__lte=end
        )
    entries = (
        LedgerEntry.objects.filter(collected)
        .exclude(settlement_status=SettlementStatus.CANCELLED)
        # `reversed_by` is a reverse one-to-one, so it select_relates like any
        # other - without it the list costs one query per row to ask whether a
        # reversal exists.
        .select_related("person", "project", "reversed_by")
        .order_by("person__last_name", "entry_date")
    )
    per_person: dict = {}
    for e in entries:
        row = per_person.setdefault(
            e.person_id,
            {"person": e.person, "deduct": Decimal("0"), "add": Decimal("0")},
        )
        if e.pay_effect == PayEffect.DEDUCT:
            row["deduct"] += e.amount
        elif e.pay_effect == PayEffect.ADD:
            row["add"] += e.amount
    for row in per_person.values():
        row["net"] = row["add"] - row["deduct"]
    return {
        "start": start,
        "end": end,
        "entries": list(entries),
        "rows": list(per_person.values()),
    }


@transaction.atomic
def include_cycle(year: int, month: int, *, actor=None) -> int:
    """Lock everything this run recovers into the cycle (OPEN -> INCLUDED).

    **Everything outstanding at the cutoff, not only this window's own dates.**
    The windows are disjoint, so when the sweep was bounded at both ends an
    entry that missed its run — dated earlier, or recorded after that window
    closed — was never picked up by any later run and stayed OPEN for ever. The
    money was reported as owed by `open_balance` and then never collected
    (ADR 0032).

    A payroll run recovers what is outstanding when it runs. That is the rule.
    """
    _start, end = cycle_bounds(year, month)
    entries = LedgerEntry.objects.select_for_update().filter(
        settlement_status=SettlementStatus.OPEN,
        entry_date__lte=end,
    )
    count = 0
    for entry in entries:
        entry.settlement_status = SettlementStatus.INCLUDED_IN_CYCLE
        entry.cycle_key = cycle_key(year, month)
        entry.save(update_fields=["settlement_status", "cycle_key"])
        count += 1
    record_event(
        actor, "ledger.cycle_included", reason=cycle_key(year, month), count=count
    )
    return count


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
        settlement_status__in=(
            SettlementStatus.OPEN,
            SettlementStatus.INCLUDED_IN_CYCLE,
        ),
    ).exclude(pay_effect=PayEffect.NONE)
    deduct = rows.filter(pay_effect=PayEffect.DEDUCT).aggregate(t=Sum("amount"))[
        "t"
    ] or Decimal("0")
    add = rows.filter(pay_effect=PayEffect.ADD).aggregate(t=Sum("amount"))[
        "t"
    ] or Decimal("0")
    return deduct - add


def guard_editable(entry: LedgerEntry) -> None:
    _require(
        not entry.is_locked,
        _("Entry is locked after cycle inclusion; record a reversal instead."),
    )
