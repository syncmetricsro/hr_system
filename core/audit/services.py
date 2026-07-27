from __future__ import annotations

from typing import Any

from core.audit.models import AuditEvent


def record_event(
    actor,
    action: str,
    *,
    target: Any | None = None,
    reason: str = "",
    **metadata: Any,
) -> AuditEvent:
    """Single sanctioned entry point for writing an audit event.

    ``actor`` may be ``None`` for system events. ``target`` may be any model
    instance; its class name and primary key are recorded.

    The event is also attributed to a **person** where one can be determined,
    because "show me everything about this worker" is a different question from
    "show me events whose target row is this worker". A certificate upload
    targets the Certificate and an equipment issue the EquipmentIssue; both are
    events about a person, and before this attribution the person filter found
    neither. Attribution also gives the log something to office-scope by.
    """
    target_type = ""
    target_id = ""
    if target is not None:
        target_type = target.__class__.__name__
        target_id = str(getattr(target, "pk", "") or "")

    actor_obj = actor if getattr(actor, "is_authenticated", False) else None
    person = _person_for(target, metadata)

    return AuditEvent.objects.create(
        actor=actor_obj,
        action=action,
        target_type=target_type,
        target_id=target_id,
        person=person,
        reason=reason,
        metadata=metadata or {},
    )


def _person_for(target: Any, metadata: dict):
    """Best-effort resolution of the worker an event concerns.

    Three sources, in order of confidence: the target *is* a person; the target
    hangs off one (``Certificate.person``, ``EquipmentIssue.person``,
    ``BlacklistCase.person``, ``ActivationApproval.person``, …); or a caller
    passed ``person=`` explicitly, which several already did as metadata.

    Deliberately forgiving - it returns ``None`` rather than raising if nothing
    resolves. An unattributed event is still a valid audit record, and writing
    audit must never be the thing that breaks a business operation.
    """
    from core.people.models import Person

    if isinstance(target, Person):
        return target

    related = getattr(target, "person", None)
    if isinstance(related, Person):
        return related

    raw = metadata.get("person")
    if isinstance(raw, Person):
        return raw
    if isinstance(raw, int) or (isinstance(raw, str) and raw.isdigit()):
        return Person.objects.filter(pk=int(raw)).first()
    return None
