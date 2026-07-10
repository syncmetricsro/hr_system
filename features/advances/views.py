from __future__ import annotations

import csv
import datetime as dt

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, require_action
from core.people.models import Person
from core.projects.models import Project
from features.advances.models import EntryType, LedgerCategory, LedgerEntry
from features.advances.services import (
    LedgerError,
    cancel_entry,
    cycle_report,
    include_cycle,
    mark_cycle_deducted,
    record_entry,
    reverse_entry,
    thursday_summary,
)


def _report_args(request) -> tuple[int, int]:
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        dt.date(year, month, 1)
    except ValueError:
        year, month = today.year, today.month
    return year, month


@require_action(Action.LEDGER_VIEW)
def ledger_overview(request):
    year, month = _report_args(request)
    return render(request, "pages/ledger.html", {
        "summary": thursday_summary(timezone.localdate()),
        "cycle": cycle_report(year, month),
        "cycle_year": year,
        "cycle_month": month,
        "entry_types": EntryType.choices,
        "categories": LedgerCategory.choices,
        "people": Person.objects.order_by("last_name", "first_name"),
        "projects": Project.objects.order_by("name"),
    })


@require_action(Action.LEDGER_ENTER)
def ledger_record(request):
    if request.method != "POST":
        return redirect("ledger_overview")
    person = get_object_or_404(Person, pk=request.POST.get("person"))
    project = None
    if request.POST.get("project"):
        project = get_object_or_404(Project, pk=request.POST["project"])
    try:
        record_entry(
            person,
            entry_type=request.POST.get("entry_type", ""),
            category=request.POST.get("category", ""),
            amount=request.POST.get("amount", "0"),
            actor=request.user,
            project=project,
            note=request.POST.get("note", "").strip(),
        )
        messages.success(request, _("Ledger entry recorded."))
    except (LedgerError, ValueError, KeyError) as exc:
        messages.error(request, str(exc) or _("Invalid ledger entry."))
    return redirect(request.POST.get("next") or "ledger_overview")


@require_action(Action.LEDGER_ENTER)
def ledger_entry_action(request, pk: int):
    if request.method != "POST":
        return redirect("ledger_overview")
    entry = get_object_or_404(LedgerEntry, pk=pk)
    action = request.POST.get("action")
    reason = request.POST.get("reason", "").strip()
    try:
        if action == "cancel":
            cancel_entry(entry, actor=request.user, reason=reason)
            messages.success(request, _("Entry cancelled."))
        elif action == "reverse":
            reverse_entry(entry, actor=request.user, reason=reason)
            messages.success(request, _("Reversal recorded."))
        else:
            messages.error(request, _("Unknown action."))
    except LedgerError as exc:
        messages.error(request, str(exc))
    return redirect(request.POST.get("next") or "ledger_overview")


@require_action(Action.LEDGER_ENTER)
def ledger_cycle_action(request):
    if request.method != "POST":
        return redirect("ledger_overview")
    year, month = int(request.POST["year"]), int(request.POST["month"])
    if request.POST.get("action") == "include":
        n = include_cycle(year, month, actor=request.user)
        messages.success(request, _("%(n)s entries included in the cycle.") % {"n": n})
    elif request.POST.get("action") == "deducted":
        n = mark_cycle_deducted(year, month, actor=request.user)
        messages.success(request, _("%(n)s entries marked settled.") % {"n": n})
    return redirect(f"{request.POST.get('next') or '/ledger/'}?year={year}&month={month}")


# --- CSV exports (layout per C-Q2/C-Q3 proposed columns) ---------------------

_CSV_COLUMNS = [
    "company", "person", "date", "entry_type", "category",
    "amount", "pay_effect", "cycle", "settlement_status",
]


def _write_entries(response, entries):
    writer = csv.writer(response)
    writer.writerow(_CSV_COLUMNS)
    for e in entries:
        writer.writerow([
            e.project.name if e.project else "",
            str(e.person),
            e.entry_date.isoformat(),
            e.entry_type,
            e.category,
            f"{e.amount}",
            e.pay_effect,
            e.cycle_key,
            e.settlement_status,
        ])
    return response


@require_action(Action.EXPORT_APPROVED)
def thursday_csv(request):
    summary = thursday_summary(timezone.localdate())
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="thursday-summary.csv"'
    return _write_entries(response, summary["entries"])


@require_action(Action.EXPORT_APPROVED)
def cycle_csv(request, year: int, month: int):
    report = cycle_report(year, month)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="cycle-{year:04d}-{month:02d}.csv"'
    return _write_entries(response, report["entries"])
