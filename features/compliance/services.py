from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.db import transaction

from core.accounts.models import Role
from core.offices.scoping import scope_people
from core.audit.services import record_event
from core.media import process_certificate_document
from core.people.models import LifecycleStatus, Person
from core.projects.models import AssignmentStatus
from features.compliance.models import Certificate

# Severity ranking for sorting (worst first).
_RANK = {"expired": 0, "missing": 1, "expiring": 2}


def add_months(d: dt.date, months: int) -> dt.date:
    """Add whole months to a date without external deps (clamps day-of-month)."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    # last day of the target month
    next_month_first = dt.date(year + (month // 12), (month % 12) + 1, 1)
    last_day = (next_month_first - dt.timedelta(days=1)).day
    return dt.date(year, month, min(d.day, last_day))


def _severity(expiry: dt.date, today: dt.date, alert_days: int) -> str | None:
    if expiry < today:
        return "expired"
    if expiry <= today + dt.timedelta(days=alert_days):
        return "expiring"
    return None


def most_relevant_certificate(certs: list[Certificate], today: dt.date) -> Certificate:
    """When a person holds more than one certificate in the same category
    (renewal history), pick the one whose icon should represent that
    category (docs/product/pill-system-design.md §2): the soonest-expiring
    non-expired row if one exists, else the most severe (most-expired) row.
    A certificate with no expiry date never expires, so it counts as valid;
    among several valid rows, a dated one sorts before an undated one only
    if it's the sole valid option's deciding factor - undated rows are
    never "urgent" so they never win over a soon-expiring dated row.
    """
    valid = [c for c in certs if c.expiry_date is None or c.expiry_date >= today]
    if valid:
        return min(valid, key=lambda c: c.expiry_date or dt.date.max)
    return min(certs, key=lambda c: c.expiry_date)


def compliance_alerts(viewer=None) -> list[dict]:
    """Missing/expiring/expired papers across workers.

    - Medical: derived from the latest readiness entry-medical date + the
      configured validity window; a Working person with no entry-medical date is
      flagged 'missing'.
    - Certificates: each certificate's expiry_date.

    A coordinator sees only people on their own active projects; every
    non-Observer role additionally sees only their own office(s)' people
    (ADR 0026 Phase B) - observer sees all.
    """
    today = dt.date.today()
    alert_days = getattr(settings, "COMPLIANCE_ALERT_DAYS", 30)
    validity_months = getattr(settings, "MEDICAL_VALIDITY_MONTHS", 12)

    people = Person.objects.filter(is_archived=False).prefetch_related(
        "readiness_records", "certificates"
    )
    # viewer=None is a deliberate "no filter" calling convention (internal/
    # test callers), distinct from user_office_scope's own None-user handling
    # (an anonymous *web* request, which fails closed to nothing) - only
    # delegate when a real viewer is present.
    if viewer is not None:
        people = scope_people(people, viewer)
    if viewer is not None and getattr(viewer, "role", None) == Role.COORDINATOR:
        people = people.filter(
            assignments__status=AssignmentStatus.ACTIVE,
            assignments__project__responsible_coordinators=viewer,
        ).distinct()

    alerts: list[dict] = []
    for person in people:
        if person.lifecycle_status == LifecycleStatus.WORKING:
            med_dates = [
                r.entry_medical_date
                for r in person.readiness_records.all()
                if r.entry_medical_date
            ]
            if not med_dates:
                alerts.append(
                    {
                        "person": person,
                        "item": "Medical",
                        "severity": "missing",
                        "due": None,
                    }
                )
            else:
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

        for cert in person.certificates.all():
            if cert.expiry_date:
                severity = _severity(cert.expiry_date, today, alert_days)
                if severity:
                    alerts.append(
                        {
                            "person": person,
                            "item": cert.name,
                            "severity": severity,
                            "due": cert.expiry_date,
                        }
                    )

    alerts.sort(key=lambda a: (_RANK[a["severity"]], a["due"] or dt.date.min))
    return alerts


# --- Certificate document CRUD (docs/product/certificate-upload-design.md) -


@transaction.atomic
def save_certificate(
    certificate: Certificate, *, actor, uploaded_file=None, creating: bool
) -> Certificate:
    """Save a certificate's metadata and, if given, its document — audited as
    a single event covering whichever changed (§5). Raises
    ``CertificateUploadError`` if ``uploaded_file`` fails validation; nothing
    is persisted in that case.
    """
    replacing_document = bool(uploaded_file)
    if uploaded_file:
        content, ext = process_certificate_document(uploaded_file)
    certificate.save()
    if uploaded_file:
        certificate.document.save(f"cert.{ext}", content, save=True)

    if creating:
        action = "certificate.uploaded"
    elif replacing_document:
        action = "certificate.replaced"
    else:
        action = "certificate.updated"
    record_event(
        actor,
        action,
        target=certificate,
        person=certificate.person_id,
        category=certificate.category,
        name=certificate.name,
    )
    return certificate


def delete_certificate(certificate: Certificate, *, actor) -> None:
    person_id = certificate.person_id
    category = certificate.category
    name = certificate.name
    pk = certificate.pk
    if certificate.document:
        certificate.document.delete(save=False)
    certificate.delete()
    record_event(
        actor,
        "certificate.deleted",
        target=None,
        certificate_id=pk,
        person=person_id,
        category=category,
        name=name,
    )
