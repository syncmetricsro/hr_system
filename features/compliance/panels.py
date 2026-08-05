"""Reports + person-card contributions of the compliance/documents feature."""

from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can
from core.dates import add_months
from core.people.permissions import can_view_sensitive
from features.compliance.models import CertificateCategory, CertificateRecordStatus
from features.compliance.services import (
    _severity,
    compliance_alerts,
    most_relevant_certificate,
)
from core.ui.registry import flag_enabled

CATEGORY_ICONS = {
    CertificateCategory.HEALTH: "cert-health",
    CertificateCategory.FORKLIFT: "cert-forklift",
    CertificateCategory.CRANE: "cert-crane",
    CertificateCategory.WELDING: "cert-welding",
    CertificateCategory.OTHER: "cert-other",
}


def compliance_tile(request):
    if not flag_enabled("documents"):
        return None
    return {
        "label": _("Compliance"),
        "value": len(compliance_alerts(request.user)),
        "url": reverse("compliance_list"),
        "tooltip_heading": _("Review compliance issues"),
        "tooltip_body": _(
            "Open workers with document or medical requirements that need attention."
        ),
    }


def compliance_badge(request):
    if not flag_enabled("documents"):
        return None
    if not getattr(request.user, "is_authenticated", False):
        return None
    alerts = compliance_alerts(request.user)
    if not alerts:
        return None
    severe = any(a["severity"] in ("expired", "missing") for a in alerts)
    return {"count": len(alerts), "severe": severe}


def medical_badge(person, today):
    """The entry medical as a badge, or None when no date has been recorded."""
    dates = [
        record.entry_medical_date
        for record in person.readiness_records.all()
        if record.entry_medical_date
    ]
    if not dates:
        return None
    expiry = add_months(max(dates), getattr(settings, "MEDICAL_VALIDITY_MONTHS", 12))
    return {
        "icon": CATEGORY_ICONS[CertificateCategory.HEALTH],
        "tooltip": _("%(name)s (expires %(date)s)")
        % {"name": _("Entry medical"), "date": expiry},
        "severity": _severity(expiry, today, 30),
    }


def certificate_badges(request, person):
    """Small icon row beside a worker's avatar, one per certificate category
    they hold - worker list and person-detail header (docs/product/
    pill-system-design.md §2, Phase 2)."""
    if not flag_enabled("documents"):
        return None
    today = dt.date.today()
    by_category: dict[str, list] = {}
    for cert in person.certificates.all():
        if cert.record_status != CertificateRecordStatus.ACTIVE:
            continue
        by_category.setdefault(cert.category, []).append(cert)

    badges = []
    # The entry medical is a date on readiness, not a Certificate row - the
    # product deliberately holds no health document (document-storage
    # boundary). It still belongs in the row of things the office reads at a
    # glance, so it is drawn from the date with the same icon and colouring.
    medical = medical_badge(person, today)
    if medical:
        badges.append(medical)

    if not by_category and not badges:
        return None

    for category, certs in by_category.items():
        best = most_relevant_certificate(certs, today)
        severity = _severity(best.expiry_date, today, 30) if best.expiry_date else None
        translated_name = _(best.name)
        if best.expiry_date:
            tooltip = _("%(name)s (expires %(date)s)") % {
                "name": translated_name,
                "date": best.expiry_date,
            }
        else:
            tooltip = translated_name
        badges.append(
            {
                "icon": CATEGORY_ICONS.get(category, "cert-other"),
                "tooltip": tooltip,
                "severity": severity,
            }
        )
    return badges


def certificate_panel(request, person):
    if not flag_enabled("documents"):
        return None
    today = dt.date.today()
    certificates = list(person.certificates.all())
    for certificate in certificates:
        certificate.severity = (
            _severity(certificate.expiry_date, today, 30)
            if certificate.expiry_date
            else None
        )
    return {
        "certificates": [
            certificate
            for certificate in certificates
            if certificate.record_status == CertificateRecordStatus.ACTIVE
        ],
        "certificate_history": [
            certificate
            for certificate in certificates
            if certificate.record_status != CertificateRecordStatus.ACTIVE
        ],
        "may_manage": can(request.user, Action.CERTIFICATE_MANAGE)
        and can_view_sensitive(request.user, person),
        "may_purge": can(request.user, Action.CERTIFICATE_PURGE_FILE)
        and can_view_sensitive(request.user, person),
        "may_view_files": can_view_sensitive(request.user, person),
    }
