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
"""

from __future__ import annotations

from django.conf import settings


def flag_enabled(name: str) -> bool:
    return getattr(settings, "FEATURE_FLAGS", {}).get(name, True)


# Each: {"template": str, "context": fn(request, person) -> dict|None, "order": int}
_person_banners: list[dict] = []
_person_panels: list[dict] = []
# Objects with .fields() -> dict[str, forms.Field] and .post_create(request, person, cleaned)
person_form_extensions: list = []
# fn(person) -> bool
exit_relevance_checks: list = []


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


def exit_relevant(person) -> bool:
    return any(check(person) for check in exit_relevance_checks)
