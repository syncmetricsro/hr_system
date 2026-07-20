from __future__ import annotations

import hashlib
import hmac
import re
import unicodedata
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from core.audit.services import record_event
from features.blacklist.models import (
    BlacklistCase,
    BlacklistCaseStatus,
    IdentifierType,
    MatchFingerprint,
)
from core.people.models import LifecycleStatus


class BlacklistError(Exception):
    """Raised on an invalid blacklist operation (e.g. deciding a closed case)."""


def _hmac_keys() -> list[str]:
    keys = getattr(settings, "BLACKLIST_HMAC_KEYS", None) or [settings.SECRET_KEY]
    return [k for k in keys if k]


# Latin letters NFKD cannot decompose to base + combining mark; folded
# explicitly so names like Groß/Łukasz survive normalization. Anything still
# non-ASCII afterwards (Cyrillic, CJK, …) is stripped by the final regex.
_FOLD = str.maketrans(
    {"ß": "SS", "ẞ": "SS", "Đ": "D", "đ": "D", "Ø": "O", "ø": "O",
     "Ł": "L", "ł": "L", "Æ": "AE", "æ": "AE", "Œ": "OE", "œ": "OE"}
)


def _normalize(identifier: str) -> str:
    """Uppercase, transliterate diacritics, and strip non-alphanumerics so
    trivial formatting/spelling differences (spaces, slashes in a rodné číslo,
    Kováč vs Kovac) don't defeat matching.

    Pure ASCII-alphanumeric input passes through unchanged, so fingerprints of
    existing stored ID codes are stable across this normalizer."""
    text = (identifier or "").upper().translate(_FOLD)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9]", "", text)


def _hmac_digest(canonical: str, *, key_version: int | None = None) -> tuple[str, int]:
    keys = _hmac_keys()
    version = len(keys) - 1 if key_version is None else key_version
    key = keys[version]
    digest = hmac.new(key.encode(), canonical.encode("utf-8"), hashlib.sha256)
    return digest.hexdigest(), version


def compute_fingerprint(identifier: str, *, key_version: int | None = None) -> tuple[str, int]:
    """Keyed HMAC-SHA256 of a normalized identifier. Returns (hex_digest, version).

    The raw identifier is used only transiently here and never stored. Defaults to
    the newest key (highest index) so new fingerprints use the current key."""
    return _hmac_digest(_normalize(identifier), key_version=key_version)


def compute_composite_identifier(
    first_name: str, last_name: str, date_of_birth, mothers_maiden_name: str
) -> str | None:
    """Canonical composite identity string for the secondary fingerprint:

        v1|<name-token-1>|…|<name-token-N>|<YYYY-MM-DD>|<MAIDEN>

    Name tokens are the whitespace/hyphen-split parts of first + last name,
    each normalized and sorted lexicographically (so first/last entry order
    can't defeat matching); the maiden name normalizes to a single token. The
    string is hashed as-is — separators keep field boundaries, so ANNA|KOVAC
    never collides with ANN|AKOVAC. Returns None when any component is missing
    or normalizes to empty (e.g. an all-Cyrillic name): no fingerprint then."""
    tokens = sorted(
        t for t in (
            _normalize(part)
            for part in re.split(r"[\s\-]+", f"{first_name or ''} {last_name or ''}")
        ) if t
    )
    maiden = _normalize(mothers_maiden_name)
    if not tokens or not date_of_birth or not maiden:
        return None
    return "|".join(["v1", *tokens, date_of_birth.isoformat(), maiden])


def compute_composite_fingerprint(canonical: str, *, key_version: int | None = None) -> tuple[str, int]:
    """HMAC of an already-canonical composite string (no re-normalization —
    it would erase the field separators)."""
    return _hmac_digest(canonical, key_version=key_version)


def check_match(identifier: str):
    """Company-wide re-entry check: return active, non-expired MatchFingerprints
    whose HMAC matches ``identifier`` under any configured key version (so rotated
    keys still match). Empty if matching is disabled or no identifier given.

    Intentionally identifier-type-agnostic (a national ID recorded as "other"
    still matches); type-aware multi-candidate checks live in check_matches."""
    if not getattr(settings, "BLACKLIST_MATCHING_ENABLED", True) or not identifier:
        return MatchFingerprint.objects.none()
    today = timezone.localdate()
    hashes = {compute_fingerprint(identifier, key_version=v)[0] for v in range(len(_hmac_keys()))}
    return (
        MatchFingerprint.objects.filter(is_active=True, hmac__in=hashes)
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gte=today))
        .select_related("person", "case")
    )


def check_matches(candidates: dict[str, str]):
    """Re-entry check over multiple fingerprint types at once. ``candidates``
    maps identifier_type → raw identifier (or, for NAME_DOB_MMN, the canonical
    composite string from compute_composite_identifier). A fingerprint matches
    only when BOTH its type and its HMAC match, so hashes never cross types.
    Same gating and expiry rules as check_match."""
    candidates = {t: v for t, v in (candidates or {}).items() if v}
    if not getattr(settings, "BLACKLIST_MATCHING_ENABLED", True) or not candidates:
        return MatchFingerprint.objects.none()
    versions = range(len(_hmac_keys()))
    match_q = Q(pk__in=[])
    for identifier_type, value in candidates.items():
        compute = (
            compute_composite_fingerprint
            if identifier_type == IdentifierType.NAME_DOB_MMN
            else compute_fingerprint
        )
        hashes = {compute(value, key_version=v)[0] for v in versions}
        match_q |= Q(identifier_type=identifier_type, hmac__in=hashes)
    today = timezone.localdate()
    return (
        MatchFingerprint.objects.filter(is_active=True)
        .filter(match_q)
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gte=today))
        .select_related("person", "case")
    )


def _retention_expiry():
    days = int(getattr(settings, "BLACKLIST_RETENTION_DAYS", 1825))
    return timezone.localdate() + timedelta(days=days)


@transaction.atomic
def propose_case(person, *, category=None, reason="", identifier=None,
                 identifier_type="national_id", composite_identifier=None, actor=None):
    """Open a proposed blacklist case (does NOT change lifecycle — a manager
    decides). If an identifier is given, store a keyed HMAC fingerprint; the raw
    identifier is discarded. ``composite_identifier`` (a canonical string from
    compute_composite_identifier) adds a secondary NAME_DOB_MMN fingerprint."""
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
    if composite_identifier:
        digest, version = compute_composite_fingerprint(composite_identifier)
        MatchFingerprint.objects.create(
            case=case, person=person, identifier_type=IdentifierType.NAME_DOB_MMN,
            hmac=digest, key_version=version, is_active=False,
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


def activation_gate(person) -> None:
    """Core activation check (registered in BlacklistConfig.ready): an
    unresolved case blocks activation. Raises the core WorkflowError so the
    caller's error handling is unchanged. Gated by the feature flag."""
    from core.projects.services import WorkflowError

    flags = getattr(settings, "FEATURE_FLAGS", {})
    if not flags.get("duplicate_blacklist", True):
        return
    if has_open_case(person):
        raise WorkflowError(
            "Blocked by an unresolved blacklist case; a manager must review it first."
        )


def purge_expired():
    """Retention purge: delete fingerprints past their expiry (raw ids were never
    stored; this drops the hashes). Returns the number deleted."""
    today = timezone.localdate()
    deleted, _ = MatchFingerprint.objects.filter(expires_at__lt=today).delete()
    return deleted
