from __future__ import annotations

from django.db import transaction
from django.db.models import Count
from django.utils.translation import gettext as _

from core.audit.models import AuditEvent
from core.audit.services import record_event
from core.people.models import LifecycleError, LifecycleStatus, Person


def inactive_by_reason(*, include_archived: bool = False) -> list[dict]:
    """Count of Inactive people grouped by their structured reason (Q5), newest
    bucket first. Null reasons fall into a 'No reason' bucket. Non-archived by
    default, matching the reports page's workforce counts."""
    qs = Person.objects.filter(lifecycle_status=LifecycleStatus.INACTIVE)
    if not include_archived:
        qs = qs.filter(is_archived=False)
    rows = []
    for r in (
        qs.values("inactive_reason__label").annotate(count=Count("id")).order_by("-count")
    ):
        rows.append({"label": r["inactive_reason__label"] or _("No reason"), "count": r["count"]})
    return rows


@transaction.atomic
def recycle_to_available(person, *, actor=None, reason: str = ""):
    """Return an Inactive person to the Available pool (exit recycling). Clears
    the structured inactive reason/since. Raises if the person is not Inactive."""
    if person.lifecycle_status != LifecycleStatus.INACTIVE:
        raise LifecycleError("Only an Inactive person can be recycled to Available.")
    person.set_status(LifecycleStatus.AVAILABLE, actor=actor, reason=reason or "recycled")
    person.inactive_reason = None
    person.inactive_since = None
    person.save(update_fields=["inactive_reason", "inactive_since", "updated_at"])
    record_event(actor, "person.recycled", target=person, reason=reason)
    return person


def person_history(person) -> list[dict]:
    """A unified, newest-first timeline of everything that happened to a person.

    Built from the domain records (trials, assignments, rooms, equipment,
    readiness, intake) plus the append-only audit log for lifecycle changes.
    """
    events: list[dict] = []

    for trial in person.trials.select_related("project"):
        events.append({"when": trial.created_at, "label": _("Trial scheduled"), "detail": trial.project.name})
        if trial.outcome_recorded_at:
            events.append({
                "when": trial.outcome_recorded_at,
                "label": _("Trial outcome"),
                "detail": f"{trial.get_outcome_display()} · {trial.project.name}",
            })

    for assignment in person.assignments.select_related("project"):
        events.append({"when": assignment.created_at, "label": _("Assigned to project"), "detail": assignment.project.name})

    for room in person.room_assignments.select_related("room__accommodation"):
        events.append({"when": room.created_at, "label": _("Room assigned"), "detail": str(room.room)})

    for issue in person.equipment_issues.select_related("item"):
        item_name = _(issue.item.name)
        events.append({
            "when": issue.issued_at,
            "label": _("Equipment issued"),
            "detail": f"{item_name} {issue.item.size}".strip(),
        })

    for readiness in person.readiness_records.select_related("project"):
        if readiness.submitted_at:
            events.append({"when": readiness.submitted_at, "label": _("Readiness submitted"), "detail": readiness.project.name})

    for intake in person.intakes.all():
        if intake.completed_at:
            events.append({"when": intake.completed_at, "label": _("Intake completed"), "detail": ""})

    lifecycle = AuditEvent.objects.filter(
        target_type="Person", target_id=str(person.pk), action="person.lifecycle_changed"
    )
    for event in lifecycle:
        events.append({
            "when": event.created_at,
            "label": _("Status changed"),
            "detail": "%(from_status)s → %(to_status)s" % {
                "from_status": _lifecycle_status_label(event.metadata.get("from_status")),
                "to_status": _lifecycle_status_label(event.metadata.get("to_status")),
            },
        })

    events.sort(key=lambda e: e["when"], reverse=True)
    return events


def _lifecycle_status_label(value: object) -> str:
    """Return a translated lifecycle label while tolerating historic data."""
    try:
        return str(LifecycleStatus(value).label)
    except ValueError:
        return str(value or "")
