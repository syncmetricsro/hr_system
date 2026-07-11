"""Checklist services (Stage C1, ADR 0022; design doc §5.5).

Business rules: instantiate the active activation template(s) for a person,
record who ticked each item, and block activation while critical items are
open. All mutations audit via ``core.audit``.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from core.audit.services import record_event
from core.ui.registry import flag_enabled
from features.checklists.models import (
    ChecklistKind,
    ChecklistTemplate,
    PersonChecklistItem,
)


def ensure_person_checklist(person, kind: str = ChecklistKind.ACTIVATION) -> list[PersonChecklistItem]:
    """Instantiate missing items of every active template of ``kind`` for the
    person (idempotent) and return the person's items of that kind."""
    templates = ChecklistTemplate.objects.filter(kind=kind, is_active=True).prefetch_related("items")
    for template in templates:
        for item in template.items.all():
            PersonChecklistItem.objects.get_or_create(person=person, item_template=item)
    return list(
        PersonChecklistItem.objects.filter(
            person=person, item_template__template__kind=kind
        ).select_related("item_template", "done_by")
    )


@transaction.atomic
def set_item_state(item: PersonChecklistItem, *, done: bool, actor=None, note: str = "") -> PersonChecklistItem:
    item.done = done
    item.done_by = actor if done else None
    item.done_at = timezone.now() if done else None
    if note:
        item.note = note
    item.save(update_fields=["done", "done_by", "done_at", "note"])
    record_event(
        actor,
        "checklist.item_ticked" if done else "checklist.item_unticked",
        target=item.person,
        reason=item.item_template.label,
    )
    return item


def missing_critical_labels(person) -> list[str]:
    """Labels of unticked critical activation items (instantiating the
    checklist on first use so a fresh person is checked against the template).
    Labels pass through gettext so seeded catalog items localize (db_trans
    pattern); operator-entered labels fall through unchanged."""
    items = ensure_person_checklist(person, ChecklistKind.ACTIVATION)
    return [_(i.item_template.label) for i in items if i.item_template.critical and not i.done]


def activation_gate(person) -> None:
    """Registered core activation check: critical items block (§5.5)."""
    from core.projects.services import WorkflowError

    if not flag_enabled("checklists"):
        return
    missing = missing_critical_labels(person)
    if missing:
        raise WorkflowError(
            _("Activation blocked by open checklist items: %(items)s") % {"items": ", ".join(missing)}
        )
