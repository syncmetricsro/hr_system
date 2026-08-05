from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.translation import gettext as _

from core.accounts.models import Role
from core.accounts.permissions import Action, can
from core.audit.services import record_event
from core.dates import add_months
from core.media import (
    CertificateUploadError,
    process_certificate_document,
    save_replacing,
)
from core.offices.scoping import scope_people
from core.people.models import LifecycleStatus, Person
from core.projects.models import AssignmentStatus
from features.compliance.models import (
    CANONICAL_CERTIFICATE_NAMES,
    FILE_ALLOWED_CATEGORIES,
    Certificate,
    CertificateRecordStatus,
)

# Severity ranking for sorting (worst first).
_RANK = {"expired": 0, "missing": 1, "expiring": 2}

# Whose lapsed medical is worth reporting. Not inactive or blacklisted: they
# are not on site, and their expiry would only crowd out the live ones.
_MEDICAL_EXPIRY_STATUSES = frozenset(
    {
        LifecycleStatus.AVAILABLE,
        LifecycleStatus.TRIAL_DAY,
        LifecycleStatus.WORKING,
    }
)


def _severity(expiry: dt.date, today: dt.date, alert_days: int) -> str | None:
    if expiry < today:
        return "expired"
    if expiry <= today + dt.timedelta(days=alert_days):
        return "expiring"
    return None


def most_relevant_certificate(certs: list[Certificate], today: dt.date) -> Certificate:
    """Pick the current certificate whose badge represents a category."""
    current = [
        certificate
        for certificate in certs
        if certificate.record_status == CertificateRecordStatus.ACTIVE
    ]
    candidates = current or certs
    valid = [
        certificate
        for certificate in candidates
        if certificate.never_expires
        or certificate.expiry_date is None
        or certificate.expiry_date >= today
    ]
    if valid:
        return min(
            valid, key=lambda certificate: certificate.expiry_date or dt.date.max
        )
    return min(
        candidates, key=lambda certificate: certificate.expiry_date or dt.date.min
    )


def compliance_alerts(viewer=None) -> list[dict]:
    """Missing/expiring/expired requirements across visible workers."""
    today = dt.date.today()
    alert_days = getattr(settings, "COMPLIANCE_ALERT_DAYS", 30)
    validity_months = getattr(settings, "MEDICAL_VALIDITY_MONTHS", 12)

    people = Person.objects.filter(is_archived=False).prefetch_related(
        "readiness_records", "certificates"
    )
    if viewer is not None:
        people = scope_people(people, viewer)
    if viewer is not None and getattr(viewer, "role", None) == Role.COORDINATOR:
        people = people.filter(
            assignments__status=AssignmentStatus.ACTIVE,
            assignments__project__responsible_coordinators=viewer,
        ).distinct()

    alerts: list[dict] = []
    for person in people:
        med_dates = [
            record.entry_medical_date
            for record in person.readiness_records.all()
            if record.entry_medical_date
        ]
        if not med_dates:
            # Only a working person is *missing* a medical. A candidate who has
            # not had one yet is not a compliance failure, and alerting on them
            # would bury the ones that are.
            if person.lifecycle_status == LifecycleStatus.WORKING:
                alerts.append(
                    {
                        "person": person,
                        "item": "Medical",
                        "severity": "missing",
                        "due": None,
                    }
                )
        elif person.lifecycle_status in _MEDICAL_EXPIRY_STATUSES:
            # A date that has lapsed is worth reporting for anyone still on the
            # books - a trial day happens on site too. Inactive and blacklisted
            # people are not going anywhere, so their expiry is noise.
            expiry = add_months(max(med_dates), validity_months)
            severity = _severity(expiry, today, alert_days)
            if severity:
                alerts.append(
                    {
                        "person": person,
                        "item": "Medical",
                        "severity": severity,
                        "due": expiry,
                    }
                )

        for certificate in person.certificates.all():
            if (
                certificate.record_status != CertificateRecordStatus.ACTIVE
                or certificate.never_expires
                or not certificate.expiry_date
            ):
                continue
            severity = _severity(certificate.expiry_date, today, alert_days)
            if severity:
                alerts.append(
                    {
                        "person": person,
                        "item": certificate.name,
                        "severity": severity,
                        "due": certificate.expiry_date,
                    }
                )

    alerts.sort(
        key=lambda alert: (_RANK[alert["severity"]], alert["due"] or dt.date.min)
    )
    return alerts


def _snapshot(certificate: Certificate | None) -> dict | None:
    if certificate is None:
        return None
    return {
        "category": certificate.category,
        "name": certificate.name,
        "issuer": certificate.issuer,
        "certificate_number": certificate.certificate_number,
        "issue_date": certificate.issue_date.isoformat()
        if certificate.issue_date
        else None,
        "expiry_date": certificate.expiry_date.isoformat()
        if certificate.expiry_date
        else None,
        "never_expires": certificate.never_expires,
        "record_status": certificate.record_status,
        "has_front": bool(certificate.front_document),
        "has_back": bool(certificate.back_document),
    }


def _delete_field_on_commit(fieldfile) -> None:
    if not fieldfile:
        return
    name = fieldfile.name
    storage = fieldfile.storage
    transaction.on_commit(lambda: storage.delete(name))


@transaction.atomic
def save_certificate(
    certificate: Certificate,
    *,
    actor,
    front_upload=None,
    back_upload=None,
    remove_back: bool = False,
    creating: bool,
    action: str | None = None,
) -> Certificate:
    """Create or update one immediately trusted occupational certificate."""
    before = None
    if certificate.pk:
        before = _snapshot(Certificate.objects.get(pk=certificate.pk))

    if certificate.category not in FILE_ALLOWED_CATEGORIES:
        raise CertificateUploadError(
            _("Files are allowed only for forklift, crane, and welding certificates.")
        )

    processed_front = (
        process_certificate_document(front_upload) if front_upload else None
    )
    processed_back = (
        process_certificate_document(back_upload, allow_pdf=False)
        if back_upload
        else None
    )

    front_ext = processed_front[1] if processed_front else ""
    existing_front_is_pdf = bool(
        certificate.front_document
        and certificate.front_document.name.lower().endswith(".pdf")
    )
    if processed_back and (
        front_ext == "pdf" or (not processed_front and existing_front_is_pdf)
    ):
        raise CertificateUploadError(_("A PDF must be the only certificate file."))
    if front_ext == "pdf" and certificate.back_document and not remove_back:
        raise CertificateUploadError(
            _(
                "Remove the current back side before replacing the certificate with a PDF."
            )
        )

    certificate.name = CANONICAL_CERTIFICATE_NAMES[certificate.category]
    certificate._pending_front_document = bool(processed_front)  # noqa: SLF001
    certificate._pending_back_document = bool(processed_back)  # noqa: SLF001
    certificate.full_clean()
    certificate.save()

    changed_files: list[str] = []
    if processed_front:
        content, extension = processed_front
        save_replacing(certificate.front_document, f"cert.{extension}", content)
        changed_files.append("front")
    if processed_back:
        content, extension = processed_back
        save_replacing(certificate.back_document, f"cert-back.{extension}", content)
        changed_files.append("back")
    elif remove_back and certificate.back_document:
        old_back = certificate.back_document
        certificate.back_document = None
        certificate.save(update_fields=["back_document"])
        _delete_field_on_commit(old_back)
        changed_files.append("back_removed")

    audit_action = action or (
        "certificate.created" if creating else "certificate.updated"
    )
    record_event(
        actor,
        audit_action,
        target=certificate,
        person=certificate.person_id,
        before=before,
        after=_snapshot(certificate),
        files_changed=changed_files,
    )
    return certificate


@transaction.atomic
def renew_certificate(
    previous: Certificate,
    replacement: Certificate,
    *,
    actor,
    front_upload,
    back_upload=None,
) -> Certificate:
    if previous.record_status != CertificateRecordStatus.ACTIVE:
        raise ValueError("Only an active certificate can be renewed.")
    replacement.person = previous.person
    replacement.category = previous.category
    replacement.supersedes = previous
    replacement.record_status = CertificateRecordStatus.ACTIVE
    saved = save_certificate(
        replacement,
        actor=actor,
        front_upload=front_upload,
        back_upload=back_upload,
        creating=True,
        action="certificate.renewed",
    )
    before = _snapshot(previous)
    previous.record_status = CertificateRecordStatus.SUPERSEDED
    previous.save(update_fields=["record_status"])
    record_event(
        actor,
        "certificate.superseded",
        target=previous,
        person=previous.person_id,
        before=before,
        after=_snapshot(previous),
        replacement_id=saved.pk,
    )
    return saved


@transaction.atomic
def archive_certificate(certificate: Certificate, *, actor, reason: str) -> Certificate:
    reason = reason.strip()
    if not reason:
        raise ValueError("An archive reason is required.")
    before = _snapshot(certificate)
    certificate.record_status = CertificateRecordStatus.ARCHIVED
    certificate.save(update_fields=["record_status"])
    record_event(
        actor,
        "certificate.archived",
        target=certificate,
        person=certificate.person_id,
        reason=reason,
        before=before,
        after=_snapshot(certificate),
    )
    return certificate


@transaction.atomic
def purge_certificate_files(
    certificate: Certificate, *, actor, reason: str
) -> Certificate:
    if not can(actor, Action.CERTIFICATE_PURGE_FILE):
        raise PermissionDenied("Only a manager may purge certificate files.")
    reason = reason.strip()
    if not reason:
        raise ValueError("A purge reason is required.")

    before = _snapshot(certificate)
    old_front = certificate.front_document
    old_back = certificate.back_document
    certificate.front_document = None
    certificate.back_document = None
    certificate.record_status = CertificateRecordStatus.ARCHIVED
    certificate.save(update_fields=["front_document", "back_document", "record_status"])
    _delete_field_on_commit(old_front)
    _delete_field_on_commit(old_back)
    record_event(
        actor,
        "certificate.files_purged",
        target=certificate,
        person=certificate.person_id,
        reason=reason,
        before=before,
        after=_snapshot(certificate),
    )
    return certificate
