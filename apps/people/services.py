from __future__ import annotations

from django.utils.translation import gettext as _

from apps.audit.models import AuditEvent


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
        events.append({"when": issue.issued_at, "label": _("Equipment issued"), "detail": str(issue.item)})

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
            "detail": f"{event.metadata.get('from_status', '')} → {event.metadata.get('to_status', '')}",
        })

    events.sort(key=lambda e: e["when"], reverse=True)
    return events
