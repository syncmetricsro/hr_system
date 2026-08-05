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
from django.utils.translation import gettext  # noqa: E402
from django.utils import translation  # noqa: E402

from core.people.models import Person  # noqa: E402
from features.advances.models import EntryType, LedgerCategory  # noqa: E402
from features.advances.models import LedgerEntry, SettlementStatus  # noqa: E402
from features.advances.services import (  # noqa: E402
    LedgerError,
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


# --- an entry can only be reversed once, and the list should say so ---------


def test_a_reversed_entry_offers_no_second_reversal(client, person, manager):
    """Reported: pressing Sztornó on an already-reversed entry answered "already
    reversed" - a refusal for an action the page was still offering, with no
    sign that the correction was already two rows below."""
    from features.advances.services import reverse_entry

    original = _advance(person, manager, "150", dt.date(2026, 8, 3))
    include_cycle(2026, 8, actor=manager)
    original.refresh_from_db()
    reverse_entry(original, actor=manager, reason="entered twice")

    original.refresh_from_db()
    assert original.is_reversed
    client.force_login(manager)

    response = client.get(reverse("ledger_overview") + "?year=2026&month=8")
    body = response.content.decode()
    # The original stays listed - reversal never deletes (C-Q5) - but its row
    # must say so, and must not offer the action a second time.
    assert "150" in body
    assert 'value="reverse"' not in body, (
        "the page still offers a reversal on an entry that already has one"
    )
    # The page renders in this client's own language, so compare against the
    # translation of the marker rather than the English source string.
    with translation.override(response.headers["Content-Language"]):
        assert gettext("Reversed") in body


def test_an_entry_not_yet_reversed_still_offers_it(client, person, manager):
    """The marker must not swallow the action for everyone else."""
    _advance(person, manager, "60", dt.date(2026, 8, 3))
    include_cycle(2026, 8, actor=manager)
    client.force_login(manager)

    body = client.get(
        reverse("ledger_overview") + "?year=2026&month=8"
    ).content.decode()

    assert 'value="reverse"' in body


# --- C-Q5 answered: deletable until paid, immutable after (ADR 0033) --------


def test_an_open_entry_can_be_deleted(person, manager):
    """A typo should not have to be carried for ever as a matched pair."""
    from features.advances.services import delete_entry

    entry = _advance(person, manager, "80", dt.date(2026, 8, 3))
    pk = entry.pk

    delete_entry(entry, actor=manager, reason="wrong person")

    assert not LedgerEntry.objects.filter(pk=pk).exists()


def test_an_included_entry_can_still_be_deleted(person, manager):
    """Included means queued for a run, not paid. The line is the money."""
    from features.advances.services import delete_entry

    entry = _advance(person, manager, "80", dt.date(2026, 8, 3))
    include_cycle(2026, 8, actor=manager)
    entry.refresh_from_db()
    assert entry.settlement_status == SettlementStatus.INCLUDED_IN_CYCLE

    delete_entry(entry, actor=manager)

    assert not LedgerEntry.objects.filter(pk=entry.pk).exists()


def test_a_settled_entry_cannot_be_deleted(person, manager):
    """Once the money has left, the ledger is what a pay dispute is argued
    from. That is the one thing C-Q5 keeps immutable."""
    from features.advances.services import delete_entry

    entry = _advance(person, manager, "80", dt.date(2026, 8, 3))
    include_cycle(2026, 8, actor=manager)
    mark_cycle_deducted(2026, 8, actor=manager)
    entry.refresh_from_db()

    with pytest.raises(LedgerError):
        delete_entry(entry, actor=manager)

    assert LedgerEntry.objects.filter(pk=entry.pk).exists()


def test_deleting_records_what_was_deleted(person, manager):
    """The row goes; the fact that it existed does not."""
    from core.audit.models import AuditEvent
    from features.advances.services import delete_entry

    entry = _advance(person, manager, "123.45", dt.date(2026, 8, 3))
    delete_entry(entry, actor=manager, reason="duplicate")

    event = AuditEvent.objects.filter(action="ledger.entry_deleted").latest("id")
    assert event.metadata["amount"] == "123.45"
    assert event.metadata["entry_date"] == "2026-08-03"
    assert event.metadata["status_was"] == SettlementStatus.OPEN


def test_a_reversed_entry_asks_for_the_reversal_to_go_first(person, manager):
    """`reversal_of` is PROTECT. Being asked to do it in two steps beats
    silently deleting a row the operator did not select."""
    from features.advances.services import delete_entry, reverse_entry

    original = _advance(person, manager, "90", dt.date(2026, 8, 3))
    include_cycle(2026, 8, actor=manager)
    original.refresh_from_db()
    reverse_entry(original, actor=manager, reason="given back")
    original.refresh_from_db()

    with pytest.raises(LedgerError):
        delete_entry(original, actor=manager)


# --- reopening a run closed by mistake --------------------------------------


def test_a_cycle_can_be_reopened_while_its_window_is_running(person, manager):
    """The misclick case: closed a run early, its window has not ended."""
    from django.utils import timezone

    from features.advances.services import reopen_cycle

    today = timezone.localdate()
    year, month = cycle_for(today)
    entry = _advance(person, manager, "70", today)
    include_cycle(year, month, actor=manager)
    entry.refresh_from_db()
    assert entry.settlement_status == SettlementStatus.INCLUDED_IN_CYCLE

    assert reopen_cycle(year, month, actor=manager) == 1

    entry.refresh_from_db()
    assert entry.settlement_status == SettlementStatus.OPEN
    assert entry.cycle_key == ""


def test_reopening_a_finished_window_is_refused_and_says_what_happens_next(
    person, manager
):
    """A refusal that only says no leaves the office stuck. This one names the
    run that will collect the entries instead."""
    from features.advances.services import reopen_cycle

    _advance(person, manager, "70", dt.date(2026, 6, 10))
    include_cycle(2026, 6, actor=manager)

    with translation.override("en"), pytest.raises(LedgerError) as excinfo:
        reopen_cycle(2026, 6, actor=manager)

    message = str(excinfo.value)
    assert "2026-06" in message and "2026-06-20" in message
    assert "2026-07" in message, f"the refusal does not name the next run: {message}"
    assert "2026-06-21" in message and "2026-07-20" in message


def test_a_settled_cycle_cannot_be_reopened(person, manager):
    """Reopening paid money is not a misclick recovery."""
    from django.utils import timezone

    from features.advances.services import reopen_cycle

    today = timezone.localdate()
    year, month = cycle_for(today)
    _advance(person, manager, "70", today)
    include_cycle(year, month, actor=manager)
    mark_cycle_deducted(year, month, actor=manager)

    with pytest.raises(LedgerError):
        reopen_cycle(year, month, actor=manager)


# --- the same table, for the whole office (2026-08-05) ----------------------
#
# The ledger page shows what a run collects. What the office is actually asked
# is what that means for each worker's pay - which existed only one profile at
# a time. The table now sits on the ledger page too, built from the same
# registered columns, so the two can never disagree.


def _overview_rows(client, year=2026, month=8):
    response = client.get(reverse("ledger_overview"), {"year": year, "month": month})
    return response.context["pay_overview"]


def test_the_ledger_page_shows_the_pay_result_for_every_worker(client, person, manager):
    record_wage(person, period="2026-08", gross_amount="700", actor=manager)
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.CASH_ADVANCE,
        amount="150",
        actor=manager,
        entry_date=dt.date(2026, 8, 5),
    )
    record_payslip(person, period="2026-08", net_amount="700", actor=manager)
    client.force_login(manager)

    overview = _overview_rows(client)

    row = next(r for r in overview["rows"] if r["period"] == "2026-08")
    amounts = [c["amount"] if c else None for c in row["cells"]]
    assert amounts == [
        Decimal("700.00"),  # gross
        Decimal("150.00"),  # ledger deductions
        Decimal("550.00"),  # after deductions
        Decimal("700.00"),  # recorded net payslip
    ]


def test_the_two_tables_on_the_page_agree(client, person, manager):
    """The reason the columns are built once and used twice.

    The cycle panel says what the run collects; the overview says what it takes
    off pay. They are the same money seen from two sides, and a worker checking
    by hand will put them side by side.
    """
    record_wage(person, period="2026-08", gross_amount="700", actor=manager)
    for entry_type, amount in (
        (EntryType.PAY_DEDUCTION, "150"),
        (EntryType.CASH_ADVANCE, "140"),
        (EntryType.PAY_ADDITION, "140"),
    ):
        record_entry(
            person,
            entry_type=entry_type,
            category=LedgerCategory.CASH_ADVANCE,
            amount=amount,
            actor=manager,
            entry_date=dt.date(2026, 8, 4),
        )
    client.force_login(manager)

    response = client.get(reverse("ledger_overview"), {"year": 2026, "month": 8})
    cycle_row = next(
        r for r in response.context["cycle"]["rows"] if r["person"].pk == person.pk
    )
    overview_row = next(
        r
        for r in response.context["pay_overview"]["rows"]
        if r["person"].pk == person.pk and r["period"] == "2026-08"
    )
    deductions = overview_row["cells"][1]["amount"]

    # 150 + 140 deducted, 140 added back.
    assert deductions == Decimal("150.00")
    assert cycle_row["net"] == -deductions


def test_the_office_wide_table_matches_the_person_page(client, person, manager):
    """Bulk and single are one code path; this is the guard that keeps it so."""
    record_wage(person, period="2026-08", gross_amount="700", actor=manager)
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount="50",
        actor=manager,
        entry_date=dt.date(2026, 8, 5),
    )
    client.force_login(manager)

    profile = _cells(client, person)
    office = next(
        r
        for r in _overview_rows(client)["rows"]
        if r["person"].pk == person.pk and r["period"] == "2026-08"
    )["cells"]

    assert [c["amount"] if c else None for c in profile] == [
        c["amount"] if c else None for c in office
    ]


def test_a_worker_with_nothing_recorded_still_gets_a_row(client, person, manager):
    """The owner asked for every worker: an omission has to be visible."""
    client.force_login(manager)

    rows = _overview_rows(client)["rows"]

    mine = [r for r in rows if r["person"].pk == person.pk]
    assert len(mine) == 3, "three runs, one row each"
    assert all(cell is None for row in mine for cell in row["cells"])


def test_the_table_covers_the_selected_run_and_the_two_before_it(
    client, person, manager
):
    client.force_login(manager)

    periods = {r["period"] for r in _overview_rows(client, 2026, 1)["rows"]}

    # January's selection reaches back across the year boundary.
    assert periods == {"2026-01", "2025-12", "2025-11"}


def test_the_derived_column_disappears_with_its_input(
    settings, client, person, manager
):
    """A client can mount the ledger without the wage book.

    Every role that may see this page holds all three view actions on
    CorvinumEU, so the interesting case is not a role - it is a client whose
    flags leave a column unsupplied. After deductions must then be absent
    rather than rendered against a missing gross.
    """
    record_entry(
        person,
        entry_type=EntryType.PAY_DEDUCTION,
        category=LedgerCategory.EQUIPMENT,
        amount="50",
        actor=manager,
        entry_date=dt.date(2026, 8, 5),
    )
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "wage_ledger": False}
    client.force_login(manager)

    response = client.get(reverse("ledger_overview"), {"year": 2026, "month": 8})

    assert response.status_code == 200
    overview = response.context["pay_overview"]
    with translation.override(response.headers["Content-Language"]):
        labels = [s["label"] for s in overview["series"]]
        assert gettext("Recorded gross wage") not in labels
        assert gettext("After deductions") not in labels
        assert gettext("Ledger deductions") in labels
    assert overview["has_derived"] is False


def test_the_overview_and_the_entry_dropdown_are_office_scoped(
    client, django_user_model
):
    """The dropdown was unscoped before this table existed.

    CorvinumEU seeds no Office rows, so nothing leaked in practice - and a
    queryset that only behaves because the data is empty is one office away
    from being a bug (ADR 0026).
    """
    from core.offices.models import Office

    mine = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    theirs = Office.objects.create(name="Győr", code="GYR", country="HU")
    manager = django_user_model.objects.create_user(
        email="scoped-mgr@demo.corvinum.test", password="x", role="manager"
    )
    manager.offices.set([mine])
    ours = Person.objects.create(first_name="Ours", last_name="Worker", office=mine)
    other = Person.objects.create(first_name="Other", last_name="Worker", office=theirs)
    client.force_login(manager)

    response = client.get(reverse("ledger_overview"), {"year": 2026, "month": 8})

    listed = {p.pk for p in response.context["people"]}
    assert ours.pk in listed and other.pk not in listed
    shown = {row["person"].pk for row in response.context["pay_overview"]["rows"]}
    assert ours.pk in shown and other.pk not in shown
