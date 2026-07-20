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
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


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
# Each: {"template": str, "context": fn(request) -> dict|None, "order": int}
_report_panels: list[dict] = []
# Each provider returns a label and period -> (Decimal, currency) values.
_person_finance_series: list[dict] = []


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


def register_report_panel(template: str, context, order: int = 100) -> None:
    entry = {"template": template, "context": context, "order": order}
    if entry not in _report_panels:
        _report_panels.append(entry)


def register_person_finance_series(provider, order: int = 100) -> None:
    entry = {"provider": provider, "order": order}
    if entry not in _person_finance_series:
        _person_finance_series.append(entry)


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


def person_finance_overview(request, person) -> dict | None:
    """Align feature-owned source values by calendar month."""
    series = []
    for entry in sorted(_person_finance_series, key=lambda item: item["order"]):
        rendered = entry["provider"](request, person)
        if rendered is not None:
            series.append(rendered)
    periods = sorted(
        {period for item in series for period in item["periods"]}, reverse=True
    )
    if not periods:
        return None
    rows = []
    for period in periods:
        cells = []
        for item in series:
            value = item["periods"].get(period)
            cells.append(
                None if value is None else {"amount": value[0], "currency": value[1]}
            )
        rows.append({"period": period, "cells": cells})
    return {"series": series, "rows": rows}


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
