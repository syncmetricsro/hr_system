"""Showing a worker what was taken off their gross wage.

The customer could not demonstrate this because the product refused to do it:
gross wage and net payslip were recorded as two independent source values and
nothing joined them (C-Q17). Since 2026-08-04 the overview also shows the
office's **own** ledger deductions and a derived *after deductions* column.

The line these tests defend is what that column is **not**. It is arithmetic on
figures this office typed in — gross minus advances, damage and equipment. It is
not net pay: no tax, no levy, no jurisdiction. The separately recorded payslip
keeps its own column precisely so the two can disagree visibly.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from django.conf import settings

# All three apps are needed: the deduction column comes from advances, the
# gross figure from wage_ledger, and the comparison column from payslips.
# Jober installs none of them, so guard on the whole set rather than one.
_REQUIRED = ("features.advances", "features.wage_ledger", "features.payslips")
if any(app not in settings.INSTALLED_APPS for app in _REQUIRED):
    pytest.skip(
        "the CorvinumEU pay stack is not installed for this client",
        allow_module_level=True,
    )

from django.urls import reverse  # noqa: E402

from core.people.models import Person  # noqa: E402
from features.advances.models import EntryType, LedgerCategory  # noqa: E402
from features.advances.models import SettlementStatus  # noqa: E402
from features.advances.services import (  # noqa: E402
    cycle_for,
    cycle_is_settled,
    cycle_report,
    include_cycle,
    mark_cycle_deducted,
    open_balance,
    record_entry,
)
from features.payslips.services import record_payslip  # noqa: E402
from features.wage_ledger.services import record_wage  # noqa: E402

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="pay-mgr@demo.corvinum.test", password="x", role="manager"
    )


@pytest.fixture
def person():
    return Person.objects.create(first_name="Fictional", last_name="Worker")


def _cells(client, person):
    response = client.get(reverse("person_detail", args=[person.pk]))
    return response.context["person_finance_overview"]["rows"][0]["cells"]


# --- the demo this exists for ----------------------------------------------


def test_gross_minus_ledger_deductions_is_shown(client, person, manager):
    """The walkthrough in the Corvinum runbook, as a test."""
    record_wage(person, period="2026-07", gross_amount="1800", actor=manager)
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="200",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount="50",
        actor=manager,
        entry_date=dt.date(2026, 7, 18),
    )
    record_payslip(person, period="2026-07", net_amount="1512.40", actor=manager)
    client.force_login(manager)

    gross, deducted, after, payslip = _cells(client, person)
    assert gross["amount"] == Decimal("1800.00")
    assert deducted["amount"] == Decimal("250.00")
    assert after["amount"] == Decimal("1550.00")
    assert after["derived"] is True
    # The payslip is *not* the derived figure, and must not be overwritten by
    # it — the gap is statutory deductions, which this product does not model.
    assert payslip["amount"] == Decimal("1512.40")
    assert payslip["derived"] is False


def test_a_pay_addition_reduces_what_was_deducted(client, person, manager):
    """Both directions land in one column, so it reads as a single number."""
    record_wage(person, period="2026-07", gross_amount="1800", actor=manager)
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="300",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    record_entry(
        person,
        entry_type=EntryType.PAY_ADDITION,
        category=LedgerCategory.TRAVEL_FUEL,
        amount="120",
        actor=manager,
        entry_date=dt.date(2026, 7, 12),
    )
    client.force_login(manager)

    _gross, deducted, after, _payslip = _cells(client, person)
    assert deducted["amount"] == Decimal("180.00")
    assert after["amount"] == Decimal("1620.00")


def test_the_derived_column_is_absent_without_a_gross_figure(client, person, manager):
    """Nothing to subtract from is not the same as zero, and printing a
    negative 'after deductions' with no wage recorded would be a lie."""
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="200",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    client.force_login(manager)

    cells = _cells(client, person)
    assert cells[2] is None, "after-deductions should be empty with no gross wage"


def test_deductions_are_grouped_by_the_run_that_collects_them(client, person, manager):
    """Reversed on 2026-08-04 (ADR 0032). This asserted grouping by the entry's
    calendar month, reasoning that all four columns should mean one period. That
    was wrong in the way that matters: an advance handed over on the 25th is
    recovered from the *next* month's pay, so showing it against the current
    month described a payslip that had already been paid."""
    record_wage(person, period="2026-08", gross_amount="1800", actor=manager)
    # A July calendar date, but the August run is what collects it.
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="90",
        actor=manager,
        entry_date=dt.date(2026, 7, 25),
    )
    client.force_login(manager)

    assert cycle_for(dt.date(2026, 7, 25)) == (2026, 8)
    _gross, deducted, after, _payslip = _cells(client, person)
    assert deducted["amount"] == Decimal("90.00")
    assert after["amount"] == Decimal("1710.00")


# --- recording an entry against the month it belongs to ---------------------


def test_the_entry_date_can_be_set_from_the_form(client, person, manager):
    """Without this the office could only ever record 'today', so a July
    deduction was impossible to enter in August — and impossible to demo."""
    client.force_login(manager)
    response = client.post(
        reverse("ledger_record"),
        {
            "person": person.pk,
            "entry_type": EntryType.PAY_DEDUCTION,
            "category": LedgerCategory.CASH_ADVANCE,
            "amount": "75",
            "entry_date": "2026-07-03",
            "note": "advance handed over on site",
        },
    )

    assert response.status_code == 302
    assert person.ledger_entries.get().entry_date == dt.date(2026, 7, 3)


def test_backdating_into_a_closed_run_is_carried_forward_not_refused(person, manager):
    """This used to raise, and refusing was the wrong answer twice over.

    It blocked ordinary present-day work on staging — equipment charges default
    to today, so once the current run was closed, issuing chargeable equipment
    stopped entirely. And it was solving a problem that carry-forward removes: a
    late entry now has somewhere to go, so there is nothing to reject (ADR 0032).
    """
    _advance(person, manager, "100", dt.date(2026, 7, 10))
    include_cycle(2026, 7, actor=manager)

    late = _advance(person, manager, "40", dt.date(2026, 7, 12))

    assert late.settlement_status == SettlementStatus.OPEN
    assert open_balance(person) == Decimal("140.00")

    include_cycle(2026, 8, actor=manager)
    late.refresh_from_db()
    assert late.cycle_key == "2026-08"


def test_todays_work_is_never_blocked_by_a_settled_cycle(person, manager):
    """The regression that reached staging: the guard refused anything landing
    in a settled cycle, including entries dated **today**.

    Equipment charges arrive through `equipment_charge_to_ledger` with no date
    at all, so they default to today - and once the current cycle had been
    marked settled, issuing chargeable equipment stopped working entirely. The
    office keeps operating regardless of where the bookkeeping has got to.
    """
    from django.utils import timezone

    today = timezone.localdate()
    # Settle the cycle that today falls into.
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="100",
        actor=manager,
        entry_date=today,
    )
    year, month = cycle_for(today)
    include_cycle(year, month, actor=manager)
    assert cycle_is_settled(today)

    # No date at all - the equipment-charge path.
    undated = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount="20",
        actor=manager,
    )
    assert undated.entry_date == today

    # And an explicit date of today, which is what the ledger form posts.
    dated = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount="30",
        actor=manager,
        entry_date=today,
    )
    assert dated.entry_date == today


def test_an_open_cycle_still_accepts_a_backdated_entry(person, manager):
    """The guard must not turn into 'no backdating at all' — recording last
    week's advance this week is the normal case."""
    entry = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="60",
        actor=manager,
        entry_date=dt.date(2026, 7, 5),
    )
    assert entry.entry_date == dt.date(2026, 7, 5)


def test_a_reversal_is_never_blocked_by_the_settled_guard(person, manager):
    """Reversal is the sanctioned correction path for a settled cycle (C-Q5).
    If the guard caught reversals there would be no correction path at all."""
    original = record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="100",
        actor=manager,
        entry_date=dt.date(2026, 7, 10),
    )
    include_cycle(2026, 7, actor=manager)
    original.refresh_from_db()

    from features.advances.services import reverse_entry

    reversal = reverse_entry(original, actor=manager, reason="entered twice")
    assert reversal.pk and reversal.reversal_of_id == original.pk


@pytest.mark.parametrize(
    "day,expected",
    [
        (dt.date(2026, 7, 1), (2026, 7)),
        (dt.date(2026, 7, 20), (2026, 7)),
        (dt.date(2026, 7, 21), (2026, 8)),
        (dt.date(2026, 12, 21), (2027, 1)),  # the year boundary
    ],
)
def test_cycle_for_matches_the_21st_to_20th_window(day, expected):
    assert cycle_for(day) == expected


# --- carry-forward: a run collects what is outstanding (ADR 0032) -----------


def _advance(person, manager, amount, on, category=LedgerCategory.CASH_ADVANCE):
    return record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=category,
        amount=amount,
        actor=manager,
        entry_date=on,
    )


def test_an_advance_that_missed_its_run_is_collected_by_the_next_one(person, manager):
    """The reported problem, end to end.

    An advance handed over on 25 July settles in the August run. If August has
    already gone out by the time it is recorded, the old sweep never touched it
    again — the windows are disjoint — so the money was owed for ever and
    collected never. September must take it.
    """
    include_cycle(2026, 8, actor=manager)  # August has already run
    late = _advance(person, manager, "250", dt.date(2026, 7, 25))
    assert late.settlement_status == SettlementStatus.OPEN

    include_cycle(2026, 9, actor=manager)

    late.refresh_from_db()
    assert late.settlement_status == SettlementStatus.INCLUDED_IN_CYCLE
    assert late.cycle_key == "2026-09"


def test_one_run_catches_up_every_stray_whatever_its_age(person, manager):
    """Strays of different ages, one run, all collected. This is the catch-up
    the first carry-forward run performs on existing data."""
    strays = [
        _advance(person, manager, "10", dt.date(2026, 5, 3)),
        _advance(person, manager, "20", dt.date(2026, 6, 17)),
        _advance(person, manager, "30", dt.date(2026, 7, 25)),
    ]

    assert include_cycle(2026, 9, actor=manager) == len(strays)
    for stray in strays:
        stray.refresh_from_db()
        assert stray.cycle_key == "2026-09", stray.entry_date


def test_open_balance_clears_once_a_run_has_collected(person, manager):
    """The arithmetic the office actually checks: owed, then not owed."""
    _advance(person, manager, "150", dt.date(2026, 7, 25))
    assert open_balance(person) == Decimal("150.00")

    include_cycle(2026, 9, actor=manager)
    mark_cycle_deducted(2026, 9, actor=manager)

    assert open_balance(person) == Decimal("0")


def test_a_run_that_has_gone_out_keeps_reporting_what_it_collected(person, manager):
    """A closed cycle is history and must not absorb later entries, however the
    sweep rules change afterwards."""
    _advance(person, manager, "100", dt.date(2026, 8, 3))
    include_cycle(2026, 8, actor=manager)
    august = cycle_report(2026, 8)
    assert [e.amount for e in august["entries"]] == [Decimal("100.00")]

    _advance(person, manager, "40", dt.date(2026, 8, 4))

    again = cycle_report(2026, 8)
    assert [e.amount for e in again["entries"]] == [Decimal("100.00")], (
        "a closed run must not pick up entries recorded after it went out"
    )


def test_a_run_not_yet_made_shows_what_it_will_collect(person, manager):
    """Before it runs, the report is a forecast — including carried strays."""
    _advance(person, manager, "60", dt.date(2026, 6, 10))
    _advance(person, manager, "70", dt.date(2026, 9, 2))

    forecast = cycle_report(2026, 9)

    assert sorted(e.amount for e in forecast["entries"]) == [
        Decimal("60.00"),
        Decimal("70.00"),
    ]


def test_the_overview_shows_a_deduction_against_the_run_that_collects_it(
    client, person, manager
):
    """The display half of the same problem: a 25 July advance is recovered from
    August pay, so it belongs in the August row, not July's."""
    record_wage(person, period="2026-08", gross_amount="1800", actor=manager)
    _advance(person, manager, "200", dt.date(2026, 7, 25))
    client.force_login(manager)

    response = client.get(reverse("person_detail", args=[person.pk]))
    rows = {
        r["period"]: r["cells"]
        for r in response.context["person_finance_overview"]["rows"]
    }

    assert "2026-08" in rows, f"expected an August row, got {sorted(rows)}"
    gross, deducted, after, _payslip = rows["2026-08"]
    assert gross["amount"] == Decimal("1800.00")
    assert deducted["amount"] == Decimal("200.00")
    assert after["amount"] == Decimal("1600.00")
