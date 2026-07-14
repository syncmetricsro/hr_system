from __future__ import annotations

from collections.abc import Iterable
from django.apps import apps
from django.db.models import Max
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _

from core.accounts.models import Role
from core.accounts.permissions import Action, can
from core.audit.models import AuditEvent
from core.audit.presentation import audit_action_label
from core.notifications.models import NotificationDismissal
from core.notifications.registry import alert_items
from core.notifications.types import NotificationItem
from core.people.models import Person
from core.projects.models import ReadinessRecord, TrialAssignment, TrialOutcome
from core.ui.registry import flag_enabled

SESSION_BASELINE_KEY = "notification_baseline_event_id"
MAX_VISIBLE_PER_GROUP = 25


def start_notification_session(request, login_event: AuditEvent) -> None:
    """Start the routine-update window at the successful login event."""
    request.session[SESSION_BASELINE_KEY] = login_event.pk


def _ensure_baseline(request) -> int:
    baseline = request.session.get(SESSION_BASELINE_KEY)
    if baseline is None:
        baseline = AuditEvent.objects.aggregate(value=Max("pk"))["value"] or 0
        request.session[SESSION_BASELINE_KEY] = baseline
    return int(baseline)


def _reverse(name: str, **kwargs) -> str:
    try:
        return reverse(name, kwargs=kwargs or None)
    except NoReverseMatch:
        return ""


def _target_object(event: AuditEvent):
    if not event.target_type or not event.target_id:
        return None
    candidates = [model for model in apps.get_models() if model.__name__ == event.target_type]
    if len(candidates) != 1:
        return None
    try:
        return candidates[0]._default_manager.filter(pk=event.target_id).first()
    except (TypeError, ValueError):
        return None


def _person_and_project(target) -> tuple[Person | None, object | None]:
    if target is None:
        return None, None
    if isinstance(target, Person):
        assignment = target.current_assignment()
        return target, assignment.project if assignment else None
    person = getattr(target, "person", None)
    project = getattr(target, "project", None)
    if person is None:
        assignment = getattr(target, "assignment", None)
        person = getattr(assignment, "person", None)
    if project is None and person is not None:
        assignment = person.current_assignment()
        project = assignment.project if assignment else None
    return person, project


def _viewer_may_see_update(user, person: Person | None, project) -> bool:
    role = getattr(user, "role", None)
    if role == Role.MANAGER:
        return True
    if role == Role.RECRUITER:
        return person is not None and person.owning_recruiter_id == user.pk
    if role == Role.COORDINATOR:
        if project is not None and project.responsible_coordinators.filter(pk=user.pk).exists():
            return True
        return person is not None and user.pk in person.responsible_coordinator_ids()
    return False


def _action_fallback_url(user, action: str) -> str:
    routes: list[tuple[str, str, Action | None]] = [
        ("equipment.", "equipment_reviews", Action.EQUIPMENT_REVIEW_DEDUCTION),
        ("blacklist.", "blacklist_queue", Action.BLACKLIST_DECIDE),
        ("finance.", "finance_summary", Action.FINANCE_VIEW_SUMMARY),
        ("ledger.", "ledger_overview", Action.LEDGER_VIEW),
        ("payslip.", "payslip_list", Action.PAYSLIP_MANAGE),
        ("accommodation.", "accommodation_list", Action.ACCOMMODATION_MANAGE),
        ("transport.", "transport_trends", Action.TRANSPORT_RECORD),
        ("feedback.", "feedback_inbox", Action.FEEDBACK_VIEW),
    ]
    for prefix, route, permission in routes:
        if action.startswith(prefix) and (permission is None or can(user, permission)):
            return _reverse(route)
    return _reverse("reports")


def _event_url(user, event: AuditEvent, person, project) -> str:
    if person is not None:
        return _reverse("person_detail", pk=person.pk)
    if project is not None:
        return _reverse("project_detail", pk=project.pk)
    return _action_fallback_url(user, event.action)


def _routine_updates(request) -> list[NotificationItem]:
    baseline = _ensure_baseline(request)
    events = (
        AuditEvent.objects.filter(pk__gt=baseline)
        .exclude(actor=request.user)
        .exclude(action__startswith="auth.")
        .select_related("actor")
        .order_by("-pk")[:100]
    )
    rendered: list[NotificationItem] = []
    for event in events:
        target = _target_object(event)
        person, project = _person_and_project(target)
        if not _viewer_may_see_update(request.user, person, project):
            continue
        url = _event_url(request.user, event, person, project)
        if not url:
            continue
        actor = event.actor.get_full_name().strip() if event.actor else ""
        if not actor and event.actor:
            actor = event.actor.email
        subject = str(person or project or _("Operational record"))
        detail = _("%(actor)s · %(subject)s") % {
            "actor": actor or _("System"),
            "subject": subject,
        }
        rendered.append(
            NotificationItem(
                key=f"audit:{event.pk}",
                version=str(event.pk),
                category="update",
                severity="info",
                title=audit_action_label(event.action),
                detail=detail,
                url=url,
                created_at=event.created_at,
            )
        )
    return rendered


def _core_alerts(request) -> Iterable[NotificationItem]:
    user = request.user
    if flag_enabled("recruitment_trials") and can(user, Action.TRIAL_RECORD_OUTCOME):
        trials = TrialAssignment.objects.filter(outcome=TrialOutcome.PENDING).select_related("person", "project")
        if getattr(user, "role", None) == Role.COORDINATOR:
            trials = trials.filter(project__responsible_coordinators=user)
        for trial in trials.distinct():
            when = trial.scheduled_for or trial.created_at
            yield NotificationItem(
                key=f"trial-outcome:{trial.pk}",
                version=f"{trial.state}:{trial.outcome}:{when.isoformat()}",
                category="alert",
                severity="warning",
                title=str(_("Trial outcome is waiting")),
                detail=f"{trial.person} · {trial.project.name}",
                url=_reverse("person_detail", pk=trial.person_id),
                created_at=when,
            )

    if flag_enabled("recruitment_trials") and can(user, Action.READINESS_COMPLETE):
        readiness = ReadinessRecord.objects.select_related("person", "project").filter(person__is_archived=False)
        if getattr(user, "role", None) == Role.COORDINATOR:
            readiness = readiness.filter(project__responsible_coordinators=user)
        for record in readiness.distinct():
            if record.is_ready():
                continue
            version = ":".join([
                record.medical_state,
                record.gear_state,
                record.accommodation_state,
                record.transport_state,
                record.updated_at.isoformat(),
            ])
            yield NotificationItem(
                key=f"readiness:{record.pk}",
                version=version,
                category="alert",
                severity="danger",
                title=str(_("Readiness needs attention")),
                detail=f"{record.person} · {record.project.name}",
                url=_reverse("person_detail", pk=record.person_id),
                created_at=record.updated_at,
            )


def all_items(request) -> list[NotificationItem]:
    if not request.user.is_authenticated or getattr(request.user, "role", None) == Role.OBSERVER:
        return []
    items = [*_core_alerts(request), *alert_items(request), *_routine_updates(request)]
    return [item for item in items if item.url]


def visible_items(request) -> dict:
    items = all_items(request)
    dismissed = set(
        NotificationDismissal.objects.filter(
            user=request.user,
            item_key__in=[item.key for item in items],
        ).values_list("item_key", "item_version")
    )
    visible = [item for item in items if (item.key, item.version) not in dismissed]
    alerts = sorted(
        (item for item in visible if item.category == "alert"),
        key=lambda item: (item.severity != "danger", -(item.created_at.timestamp() if item.created_at else 0)),
    )
    updates = sorted(
        (item for item in visible if item.category == "update"),
        key=lambda item: item.created_at or 0,
        reverse=True,
    )
    return {
        "enabled": True,
        "alerts": alerts[:MAX_VISIBLE_PER_GROUP],
        "updates": updates[:MAX_VISIBLE_PER_GROUP],
        "alert_count": len(alerts),
        "update_count": len(updates),
        "total_count": len(alerts) + len(updates),
    }


def dismiss_item(request, key: str, version: str) -> bool:
    """Dismiss only an item the server recomputes as visible to this user."""
    match = next((item for item in all_items(request) if item.key == key and item.version == version), None)
    if match is None:
        return False
    NotificationDismissal.objects.get_or_create(
        user=request.user,
        item_key=match.key,
        item_version=match.version,
    )
    return True
