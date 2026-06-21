from __future__ import annotations

from typing import Any

from apps.audit.models import AuditEvent


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
    """
    target_type = ""
    target_id = ""
    if target is not None:
        target_type = target.__class__.__name__
        target_id = str(getattr(target, "pk", "") or "")

    actor_obj = actor if getattr(actor, "is_authenticated", False) else None

    return AuditEvent.objects.create(
        actor=actor_obj,
        action=action,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        metadata=metadata or {},
    )
