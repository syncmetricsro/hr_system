from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from django.utils import timezone

from core.people.models import Person
from features.advances.models import (
    EntryType,
    LedgerEntry,
    PayEffect,
    SettlementStatus,
)
from features.advances.services import (
    LedgerError,
    cancel_entry,
    cycle_bounds,
    cycle_report,
    include_cycle,
    mark_cycle_deducted,
    open_balance,
    record_entry,
    reverse_entry,
    thursday_summary,
    week_cutoff,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="lg-manager@demo.jober.test", password="x", role="manager"
    )


@pytest.fixture
def person():
    return Person.objects.create(first_name="Ledger", last_name="Person")


def test_pay_effect_mapping_enforced(person, manager):
    entry = record_entry(
        person, entry_type=EntryType.CASH_ADVANCE, category="cash_advance",
        amount=Decimal("100"), actor=manager,
    )
    assert entry.pay_effect == PayEffect.DEDUCT
    with pytest.raises(LedgerError):
        record_entry(
            person, entry_type=EntryType.PAY_ADDITION, category="travel_fuel",
            amount=Decimal("30"), actor=manager, pay_effect=PayEffect.DEDUCT,
        )


def test_amount_must_be_positive(person, manager):
    with pytest.raises(LedgerError):
        record_entry(
            person, entry_type=EntryType.CASH_ADVANCE, category="cash_advance",
            amount=Decimal("-100"), actor=manager,
        )


def test_week_cutoff_is_thursday_1400_local(person):
    # 2026-07-06 is a Monday; its week's cut-off is Thursday 2026-07-09 14:00.
    cutoff = week_cutoff(dt.date(2026, 7, 6))
    local = timezone.localtime(cutoff)
    assert (local.year, local.month, local.day, local.hour) == (2026, 7, 9, 14)


def test_thursday_summary_rolls_late_entries(person, manager):
    entry = record_entry(
        person, entry_type=EntryType.CASH_ADVANCE, category="cash_advance",
        amount=Decimal("50"), actor=manager,
    )
    now = timezone.localtime()
    cutoff = week_cutoff(now.date())

    # Entry created before this week's cut-off appears in this week's summary…
    LedgerEntry.objects.filter(pk=entry.pk).update(created_at=cutoff - dt.timedelta(hours=1))
    assert [e.pk for e in thursday_summary(now.date())["entries"]] == [entry.pk]

    # …created after the cut-off it rolls to next week, never retro-inserted.
    LedgerEntry.objects.filter(pk=entry.pk).update(created_at=cutoff + dt.timedelta(hours=1))
    assert thursday_summary(now.date())["entries"] == []
    assert [e.pk for e in thursday_summary(now.date() + dt.timedelta(days=7))["entries"]] == [entry.pk]


def test_cycle_bounds_cross_year():
    start, end = cycle_bounds(2027, 1)
    assert start == dt.date(2026, 12, 21)
    assert end == dt.date(2027, 1, 20)


def test_cycle_report_nets_positive_magnitudes(person, manager):
    record_entry(person, entry_type=EntryType.CASH_ADVANCE, category="cash_advance",
                 amount=Decimal("100"), actor=manager, entry_date=dt.date(2026, 7, 1))
    record_entry(person, entry_type=EntryType.PAY_DEDUCTION, category="clothing",
                 amount=Decimal("25"), actor=manager, entry_date=dt.date(2026, 7, 10))
    record_entry(person, entry_type=EntryType.PAY_ADDITION, category="travel_fuel",
                 amount=Decimal("30"), actor=manager, entry_date=dt.date(2026, 7, 15))
    report = cycle_report(2026, 7)
    row = report["rows"][0]
    assert row["deduct"] == Decimal("125")
    assert row["add"] == Decimal("30")
    assert row["net"] == Decimal("-95")
    assert all(e.amount > 0 for e in report["entries"])


def test_inclusion_locks_and_settles(person, manager):
    entry = record_entry(person, entry_type=EntryType.CASH_ADVANCE, category="cash_advance",
                         amount=Decimal("100"), actor=manager, entry_date=dt.date(2026, 7, 1))
    assert include_cycle(2026, 7, actor=manager) == 1
    entry.refresh_from_db()
    assert entry.settlement_status == SettlementStatus.INCLUDED_IN_CYCLE
    assert entry.cycle_key == "2026-07"
    with pytest.raises(LedgerError):
        cancel_entry(entry, actor=manager)  # locked -> reversal is the only path
    assert mark_cycle_deducted(2026, 7, actor=manager) == 1
    entry.refresh_from_db()
    assert entry.settlement_status == SettlementStatus.DEDUCTED


def test_cancel_only_open(person, manager):
    entry = record_entry(person, entry_type=EntryType.CASH_ADVANCE, category="cash_advance",
                         amount=Decimal("10"), actor=manager)
    cancel_entry(entry, actor=manager)
    entry.refresh_from_db()
    assert entry.settlement_status == SettlementStatus.CANCELLED
    # Cancelled entries leave the reports.
    assert cycle_report(timezone.localdate().year, timezone.localdate().month)["entries"] == [] or all(
        e.pk != entry.pk for e in cycle_report(timezone.localdate().year, timezone.localdate().month)["entries"]
    )


def test_reversal_creates_opposite_linked_entry(person, manager):
    entry = record_entry(person, entry_type=EntryType.PAY_DEDUCTION, category="equipment",
                         amount=Decimal("25"), actor=manager, entry_date=dt.date(2026, 7, 5))
    include_cycle(2026, 7, actor=manager)
    entry.refresh_from_db()
    reversal = reverse_entry(entry, actor=manager, reason="returned after all")
    assert reversal.entry_type == EntryType.PAY_ADDITION
    assert reversal.pay_effect == PayEffect.ADD
    assert reversal.amount == Decimal("25")
    assert reversal.reversal_of == entry
    with pytest.raises(LedgerError):
        reverse_entry(entry, actor=manager)  # only once


def test_open_balance(person, manager):
    record_entry(person, entry_type=EntryType.CASH_ADVANCE, category="cash_advance",
                 amount=Decimal("100"), actor=manager)
    record_entry(person, entry_type=EntryType.PAY_ADDITION, category="travel_fuel",
                 amount=Decimal("30"), actor=manager)
    assert open_balance(person) == Decimal("70")
