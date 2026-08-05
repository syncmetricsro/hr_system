"""Surface registry (Stage B, ADR 0021).

Core owns the UI composition points; feature apps register contributions from
``AppConfig.ready()`` so dependencies point feature -> core only. A feature
whose flag is off simply contributes nothing (its context fn returns None, or
it skips registration).

Slots:
- person banners  — alert strips at the top of the person card
- person panels   — sections on the person card
- form extensions — extra intake-form fields + post-create handlers
- exit relevance  — "does this person still hold feature resources?" checks
- finance series  — period-keyed person money data merged by core
- person badges   — small icon row beside a person's avatar (list + detail)
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _


def flag_enabled(name: str) -> bool:
    return getattr(settings, "FEATURE_FLAGS", {}).get(name, True)


# Each: {"template": str, "context": fn(request, person) -> dict|None, "order": int}
_person_banners: list[dict] = []
_person_panels: list[dict] = []
# Objects with .fields() -> dict[str, forms.Field] and .post_create(request, person, cleaned)
person_form_extensions: list = []
# fn(person) -> bool
exit_relevance_checks: list = []
# Each: {"context": fn(request) -> dict|None, "order": int} -> {"label","value"}
_report_tiles: list[dict] = []
_staff_activity_panels: list[dict] = []
# Each: {"template": str, "context": fn(request) -> dict|None, "order": int}
_report_panels: list[dict] = []
# Each provider returns a label and period -> (Decimal, currency) values.
_person_finance_series: list[dict] = []
# Keyed by nav-tab slot ("compliance", "reviews", ...); each entry:
# {"context": fn(request) -> {"count": int, "severe": bool}|None, "order": int}
_nav_badges: dict[str, list[dict]] = {}
# Each: {"context": fn(request, person) -> list[dict]|None, "order": int}.
# Each returned dict: {"icon": str, "tooltip": str, "severity": "expired"|"expiring"|None}
_person_badges: list[dict] = []


def register_person_banner(template: str, context, order: int = 100) -> None:
    entry = {"template": template, "context": context, "order": order}
    if entry not in _person_banners:
        _person_banners.append(entry)


def register_person_panel(template: str, context, order: int = 100) -> None:
    entry = {"template": template, "context": context, "order": order}
    if entry not in _person_panels:
        _person_panels.append(entry)


def register_person_form_extension(extension) -> None:
    if extension not in person_form_extensions:
        person_form_extensions.append(extension)


def register_exit_relevance(fn) -> None:
    if fn not in exit_relevance_checks:
        exit_relevance_checks.append(fn)


def register_report_tile(context, order: int = 100) -> None:
    entry = {"context": context, "order": order}
    if entry not in _report_tiles:
        _report_tiles.append(entry)


def register_staff_activity_panel(template: str, context, order: int = 100) -> None:
    """A feature's contribution to the Staff activity page (J2).

    Core owns the page and the recruiter figures, which come from
    `core.people`; anything drawn from a feature's own records - equipment
    issuance, accommodation transfers - arrives through here, so core never
    imports a feature in order to report on it.
    """
    entry = {"template": template, "context": context, "order": order}
    if entry not in _staff_activity_panels:
        _staff_activity_panels.append(entry)


def register_report_panel(template: str, context, order: int = 100) -> None:
    entry = {"template": template, "context": context, "order": order}
    if entry not in _report_panels:
        _report_panels.append(entry)


def register_person_finance_series(
    provider, order: int = 100, role: str = "source", key: str = ""
) -> None:
    """Register a per-person, per-period money column.

    ``role`` lets core relate two columns without knowing which feature
    supplies either. ``"gross"`` and ``"deduction"`` together produce the
    derived *after deductions* column; the default ``"source"`` is a column
    that stands alone and is never arithmetic input.

    ``key`` names the column in a sort URL. It is stable and independent of
    position, because which columns exist depends on the client's flags and the
    reader's permissions — a shared link that sorts "the third column" would
    sort a different figure for the next person who opens it.

    **The provider is bulk**::

        provider(request, people) -> {"label": str, "by_person": {
            person_id: {period_key: (amount, currency)}
        }} | None

    It takes an iterable of people because the same columns are drawn one
    person at a time on a profile and for a whole office on the ledger page.
    A per-person signature would have meant three queries per worker there, and
    the alternative - a second bulk implementation - is how two screens start
    disagreeing about one number.
    """
    entry = {
        "provider": provider,
        "order": order,
        "role": role,
        "key": key or role,
    }
    if entry not in _person_finance_series:
        _person_finance_series.append(entry)


def register_nav_badge(slot: str, context, order: int = 100) -> None:
    """Register an attention-count provider for a nav tab (docs/product/
    pill-system-design.md §3), e.g. ``register_nav_badge("compliance", ...)``.
    ``context(request) -> {"count": int, "severe": bool} | None``."""
    entry = {"context": context, "order": order}
    bucket = _nav_badges.setdefault(slot, [])
    if entry not in bucket:
        bucket.append(entry)


def register_person_badges(context, order: int = 100) -> None:
    """Register a small-icon-row provider for a person, shown on both the
    worker list and the person-detail header (docs/product/
    pill-system-design.md §2's deferred Phase 2 - the list-row slot that
    didn't exist when §1/§3 shipped). ``context(request, person) ->
    list[{"icon": str, "tooltip": str, "severity": str|None}] | None``."""
    entry = {"context": context, "order": order}
    if entry not in _person_badges:
        _person_badges.append(entry)


def person_badges(request, person) -> list[dict]:
    badges: list[dict] = []
    for entry in sorted(_person_badges, key=lambda e: e["order"]):
        result = entry["context"](request, person)
        if result:
            badges.extend(result)
    return badges


def nav_badge(request, slot: str) -> dict | None:
    for entry in sorted(_nav_badges.get(slot, []), key=lambda e: e["order"]):
        ctx = entry["context"](request)
        if ctx is not None:
            return ctx
    return None


def _render_slot(slot: list[dict], request, person) -> list[dict]:
    rendered = []
    for entry in sorted(slot, key=lambda e: e["order"]):
        ctx = entry["context"](request, person)
        if ctx is None:
            continue
        rendered.append({"template": entry["template"], "person": person, **ctx})
    return rendered


def person_banners(request, person) -> list[dict]:
    return _render_slot(_person_banners, request, person)


def person_panels(request, person) -> list[dict]:
    return _render_slot(_person_panels, request, person)


def _finance_series(request, people):
    """Every registered column, in order, for these people.

    Returns ``[{label, role, by_person}]`` with the derived *after deductions*
    column already inserted where both its inputs exist. One definition, so the
    profile table and the office-wide table cannot disagree.
    """
    series = []
    for entry in sorted(_person_finance_series, key=lambda item: item["order"]):
        rendered = entry["provider"](request, people)
        if rendered is not None:
            series.append({**rendered, "role": entry["role"], "key": entry["key"]})

    gross = next((s for s in series if s["role"] == "gross"), None)
    deduction = next((s for s in series if s["role"] == "deduction"), None)
    if gross is None or deduction is None:
        return series

    derived = {
        "label": _("After deductions"),
        "role": "derived",
        "key": "after_deductions",
        "by_person": {},
    }
    for person_id, periods in gross["by_person"].items():
        taken = deduction["by_person"].get(person_id, {})
        for period, (base, currency) in periods.items():
            owed = taken.get(period)
            derived["by_person"].setdefault(person_id, {})[period] = (
                base - (owed[0] if owed else 0),
                currency,
            )
    # Immediately after the deductions it is computed from, so the table reads
    # left to right as: gross, taken off, what is left, what payroll actually
    # paid. Appending it last would put the arithmetic after its own comparison
    # figure.
    series.insert(series.index(deduction) + 1, derived)
    return series


def _cells(series, person_id, period):
    cells = []
    for item in series:
        value = item["by_person"].get(person_id, {}).get(period)
        cells.append(
            None
            if value is None
            else {
                "amount": value[0],
                "currency": value[1],
                "derived": item["role"] == "derived",
            }
        )
    return cells


def person_finance_overview(request, person) -> dict | None:
    """Align feature-owned source values for one person.

    Where a ``gross`` column and a ``deduction`` column are both present, a
    derived **after deductions** column is appended. That subtraction is the
    company's own recorded money only — the deductions it entered against a
    gross figure it entered. It is deliberately **not** net pay: no tax or levy
    is involved, and the separately recorded net payslip stays its own column so
    the two can be compared rather than conflated (C-Q17).

    The one-person case of `finance_overview_table`.
    """
    series = _finance_series(request, [person])
    periods = sorted(
        {period for item in series for period in item["by_person"].get(person.pk, {})},
        reverse=True,
    )
    if not periods:
        return None
    rows = [
        {"period": period, "cells": _cells(series, person.pk, period)}
        for period in periods
    ]
    has_derived = any(item["role"] == "derived" for item in series)
    return {"series": series, "rows": rows, "has_derived": has_derived}


#: Columns that are not one of the registered money series.
FINANCE_SORT_PERSON = "person"
FINANCE_SORT_PERIOD = "period"


def _sort_rows(rows, series, sort: str, descending: bool):
    """Order the table by one column, with empties always last.

    A dash is not a zero — it means nothing was recorded — so an empty cell
    sorts to the bottom in **both** directions. Sorting descending by
    deductions to find the largest, and being handed a screenful of blanks
    first, would make the control useless for the one question it answers.
    """
    if sort == FINANCE_SORT_PERIOD:
        rows.sort(
            key=lambda row: (row["period"], str(row["person"])), reverse=descending
        )
        return rows

    index = next(
        (i for i, item in enumerate(series) if item["key"] == sort),
        None,
    )
    if index is None:
        # Default, and the fallback for a stale or hand-edited sort key: by
        # person, newest run first. Never an error - a bad URL should show the
        # table, not a 500.
        rows.sort(key=lambda row: (str(row["person"]), _descending(row["period"])))
        return rows

    def money(row):
        cell = row["cells"][index]
        return None if cell is None else cell["amount"]

    rows.sort(key=lambda row: (str(row["person"]), row["period"]))
    rows.sort(
        key=lambda row: (money(row) is None, _flip(money(row), descending)),
    )
    return rows


def _flip(amount, descending):
    if amount is None:
        return 0
    return -amount if descending else amount


def _descending(period: str) -> str:
    """Sort a YYYY-MM string newest-first inside an ascending sort."""
    return "".join(chr(255 - ord(character)) for character in period)


def finance_overview_table(
    request, people, periods, sort: str = "", descending: bool = False
) -> dict | None:
    """The same columns, for a whole office: one row per worker per period.

    ``periods`` is given rather than discovered, because this table answers
    "what does the run I am looking at mean for each worker" — the caller owns
    which runs those are. Every person passed in gets a row per period, empty
    cells included: a worker with no gross wage recorded is exactly what an
    office needs to see.

    ``sort`` is a column ``key`` (or ``person``/``period``); an unknown one
    falls back to the default order rather than failing.
    """
    people = list(people)
    if not people:
        return None
    series = _finance_series(request, people)
    if not series:
        return None
    rows = [
        {"person": person, "period": period, "cells": _cells(series, person.pk, period)}
        for person in people
        for period in periods
    ]
    _sort_rows(rows, series, sort, descending)
    return {
        "series": series,
        "rows": rows,
        "sort": sort or FINANCE_SORT_PERSON,
        "descending": descending,
        "has_derived": any(item["role"] == "derived" for item in series),
    }


def exit_relevant(person) -> bool:
    return any(check(person) for check in exit_relevance_checks)


def report_tiles(request) -> list[dict]:
    tiles = []
    for entry in sorted(_report_tiles, key=lambda e: e["order"]):
        ctx = entry["context"](request)
        if ctx is not None:
            if ctx.get("url") and not all(
                ctx.get(key) for key in ("tooltip_heading", "tooltip_body")
            ):
                raise ImproperlyConfigured(
                    "Linked report tiles require tooltip_heading and tooltip_body."
                )
            tiles.append(ctx)
    return tiles


def report_panels(request) -> list[dict]:
    rendered = []
    for entry in sorted(_report_panels, key=lambda e: e["order"]):
        ctx = entry["context"](request)
        if ctx is not None:
            rendered.append({"template": entry["template"], **ctx})
    return rendered


def staff_activity_panels(request) -> list[dict]:
    rendered = []
    for entry in sorted(_staff_activity_panels, key=lambda e: e["order"]):
        ctx = entry["context"](request)
        if ctx is not None:
            rendered.append({"template": entry["template"], **ctx})
    return rendered
