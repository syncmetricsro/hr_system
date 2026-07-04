from __future__ import annotations

import hashlib
import hmac
import re
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.audit.services import record_event
from apps.blacklist.models import (
    BlacklistCase,
    BlacklistCaseStatus,
    MatchFingerprint,
)
from apps.people.models import LifecycleStatus


class BlacklistError(Exception):
    """Raised on an invalid blacklist operation (e.g. deciding a closed case)."""


def _hmac_keys() -> list[str]:
    keys = getattr(settings, "BLACKLIST_HMAC_KEYS", None) or [settings.SECRET_KEY]
    return [k for k in keys if k]


def _normalize(identifier: str) -> str:
    """Uppercase and strip non-alphanumerics so trivial formatting differences
    (spaces, slashes in a rodné číslo) don't defeat matching."""
    return re.sub(r"[^A-Za-z0-9]", "", identifier or "").upper()


def compute_fingerprint(identifier: str, *, key_version: int | None = None) -> tuple[str, int]:
    """Keyed HMAC-SHA256 of a normalized identifier. Returns (hex_digest, version).

    The raw identifier is used only transiently here and never stored. Defaults to
    the newest key (highest index) so new fingerprints use the current key."""
    keys = _hmac_keys()
    version = len(keys) - 1 if key_version is None else key_version
    key = keys[version]
    digest = hmac.new(key.encode(), _normalize(identifier).encode("utf-8"), hashlib.sha256)
    return digest.hexdigest(), version


def check_match(identifier: str):
    """Company-wide re-entry check: return active, non-expired MatchFingerprints
    whose HMAC matches ``identifier`` under any configured key version (so rotated
    keys still match). Empty if matching is disabled or no identifier given."""
    if not getattr(settings, "BLACKLIST_MATCHING_ENABLED", True) or not identifier:
        return MatchFingerprint.objects.none()
    today = timezone.localdate()
    hashes = {compute_fingerprint(identifier, key_version=v)[0] for v in range(len(_hmac_keys()))}
    return (
        MatchFingerprint.objects.filter(is_active=True, hmac__in=hashes)
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gte=today))
        .select_related("person", "case")
    )


def _retention_expiry():
    days = int(getattr(settings, "BLACKLIST_RETENTION_DAYS", 1825))
    return timezone.localdate() + timedelta(days=days)


@transaction.atomic
def propose_case(person, *, category=None, reason="", identifier=None,
                 identifier_type="national_id", actor=None):
    """Open a proposed blacklist case (does NOT change lifecycle — a manager
    decides). If an identifier is given, store a keyed HMAC fingerprint; the raw
    identifier is discarded."""
    case = BlacklistCase.objects.create(
        person=person,
        status=BlacklistCaseStatus.PROPOSED,
        category=category,
        restricted_reason=reason or "",
        proposed_by=actor if getattr(actor, "is_authenticated", False) else None,
        expiry_date=_retention_expiry(),
    )
    if identifier:
        digest, version = compute_fingerprint(identifier)
        MatchFingerprint.objects.create(
            case=case, person=person, identifier_type=identifier_type,
            hmac=digest, key_version=version, is_active=False,  # activated on approval
            expires_at=_retention_expiry(),
        )
    record_event(actor, "blacklist.proposed", target=case, person=str(person))
    return case


@transaction.atomic
def decide_case(case, decision, *, actor=None, reason=""):
    """Manager decision on a proposed case. ``approve`` moves the person to
    BLACKLISTED and activates the fingerprint; ``reject`` closes it with no
    lifecycle change. Audited."""
    if case.status != BlacklistCaseStatus.PROPOSED:
        raise BlacklistError("Only a proposed case can be decided.")
    if decision == "approve":
        case.status = BlacklistCaseStatus.APPROVED
        case.person.set_status(LifecycleStatus.BLACKLISTED, actor=actor, reason=reason or "blacklisted")
        case.fingerprints.update(is_active=True)
    elif decision == "reject":
        case.status = BlacklistCaseStatus.REJECTED
    else:
        raise BlacklistError("Decision must be 'approve' or 'reject'.")
    if reason:
        case.restricted_reason = reason
    case.decided_by = actor if getattr(actor, "is_authenticated", False) else None
    case.decided_at = timezone.now()
    case.save(update_fields=["status", "restricted_reason", "decided_by", "decided_at", "updated_at"])
    record_event(actor, "blacklist.decided", target=case, decision=decision)
    return case


@transaction.atomic
def remove_case(case, *, actor=None, reason=""):
    """Lift an approved blacklist: revoke fingerprints and return the person to
    Available. Manager only. A reason is recorded in the audit trail."""
    if case.status != BlacklistCaseStatus.APPROVED:
        raise BlacklistError("Only an approved case can be removed.")
    case.status = BlacklistCaseStatus.REMOVED
    case.fingerprints.update(is_active=False)
    if case.person.lifecycle_status == LifecycleStatus.BLACKLISTED:
        case.person.set_status(LifecycleStatus.AVAILABLE, actor=actor, reason=reason or "blacklist removed")
    case.decided_by = actor if getattr(actor, "is_authenticated", False) else None
    case.decided_at = timezone.now()
    case.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])
    record_event(actor, "blacklist.removed", target=case, reason=reason)
    return case


def has_open_case(person) -> bool:
    """True if the person has an unresolved (proposed/approved) case — used to
    hard-gate activation (plan §12.13)."""
    return person.blacklist_cases.filter(
        status__in=(BlacklistCaseStatus.PROPOSED, BlacklistCaseStatus.APPROVED)
    ).exists()


def purge_expired():
    """Retention purge: delete fingerprints past their expiry (raw ids were never
    stored; this drops the hashes). Returns the number deleted."""
    today = timezone.localdate()
    deleted, _ = MatchFingerprint.objects.filter(expires_at__lt=today).delete()
    return deleted
