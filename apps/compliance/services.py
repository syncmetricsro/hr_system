from __future__ import annotations

import datetime as dt

from django.conf import settings

from apps.accounts.models import Role
from apps.people.models import LifecycleStatus, Person
from apps.projects.models import AssignmentStatus

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


def compliance_alerts(viewer=None) -> list[dict]:
    """Missing/expiring/expired papers across workers.

    - Medical: derived from the latest readiness entry-medical date + the
      configured validity window; a Working person with no entry-medical date is
      flagged 'missing'.
    - Certificates: each certificate's expiry_date.

    A coordinator sees only people on their own active projects; managers and
    observers see all.
    """
    today = dt.date.today()
    alert_days = getattr(settings, "COMPLIANCE_ALERT_DAYS", 30)
    validity_months = getattr(settings, "MEDICAL_VALIDITY_MONTHS", 12)

    people = (
        Person.objects.filter(is_archived=False)
        .prefetch_related("readiness_records", "certificates")
    )
    if viewer is not None and getattr(viewer, "role", None) == Role.COORDINATOR:
        people = people.filter(
            assignments__status=AssignmentStatus.ACTIVE,
            assignments__project__responsible_coordinators=viewer,
        ).distinct()

    alerts: list[dict] = []
    for person in people:
        if person.lifecycle_status == LifecycleStatus.WORKING:
            med_dates = [r.entry_medical_date for r in person.readiness_records.all() if r.entry_medical_date]
            if not med_dates:
                alerts.append({"person": person, "item": "Medical", "severity": "missing", "due": None})
            else:
                expiry = add_months(max(med_dates), validity_months)
                severity = _severity(expiry, today, alert_days)
                if severity:
                    alerts.append({"person": person, "item": "Medical", "severity": severity, "due": expiry})

        for cert in person.certificates.all():
            if cert.expiry_date:
                severity = _severity(cert.expiry_date, today, alert_days)
                if severity:
                    alerts.append({"person": person, "item": cert.name, "severity": severity, "due": cert.expiry_date})

    alerts.sort(key=lambda a: (_RANK[a["severity"]], a["due"] or dt.date.min))
    return alerts
