"""Payslip services (Stage C5, ADR 0023).

A minimal stdlib PDF writer produces the one-page payslip; pypdf applies
PDF 2.0 AES-256 (R6) with a per-send random password. The password is
returned to the caller for one-time display and out-of-band delivery —
it is never stored, never logged, never emailed.
"""

from __future__ import annotations

import io
import secrets
from smtplib import SMTPException

from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.translation import gettext as _

from core.audit.services import record_event

# No 0/O/1/l/I — read-aloud safe (ADR 0023).
PASSWORD_ALPHABET = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ"
PASSWORD_GROUPS = 3
PASSWORD_GROUP_LEN = 4


class PayslipError(Exception):
    pass


def record_payslip(
    person,
    *,
    period: str,
    net_amount,
    note: str = "",
    issue_date=None,
    actor=None,
):
    """Create a payslip record (audited — a pay amount must never appear
    without an audit trail; conformance finding 2026-07-11)."""
    from django.db import transaction

    from features.payslips.models import Payslip

    with transaction.atomic():
        payslip = Payslip(
            person=person,
            period=period,
            net_amount=net_amount or None,
            note=note,
            issue_date=issue_date or timezone.localdate(),
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        payslip.full_clean()
        payslip.save()
        record_event(
            actor, "payslip.recorded", target=person,
            reason=(
                f"{period} {payslip.net_amount} {payslip.currency} "
                f"issued {payslip.issue_date.isoformat()}"
            ),
            issue_date=payslip.issue_date.isoformat(),
            period=period,
            net_amount=str(payslip.net_amount),
            currency=payslip.currency,
        )
    return payslip


def generate_password() -> str:
    groups = (
        "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_GROUP_LEN))
        for _ in range(PASSWORD_GROUPS)
    )
    return "-".join(groups)


def _pdf_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _simple_pdf(lines: list[str]) -> bytes:
    """One A4 page of Helvetica text — plain stdlib, no content library."""
    stream_parts = ["BT", "/F1 12 Tf", "72 770 Td", "16 TL"]
    for line in lines:
        stream_parts.append(f"({_pdf_escape(line)}) Tj T*")
    stream_parts.append("ET")
    stream = "\n".join(stream_parts).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode())
        out.write(obj)
        out.write(b"\nendobj\n")
    xref_at = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode()
    )
    return out.getvalue()


def build_encrypted_pdf(payslip, password: str) -> bytes:
    from pypdf import PdfReader, PdfWriter

    lines = [
        "PAYSLIP",
        "",
        f"Worker: {payslip.person}",
        f"Period: {payslip.period}",
        f"Net amount paid: {payslip.net_amount} {payslip.currency}",
    ]
    if payslip.note:
        lines += ["", f"Note: {payslip.note}"]
    lines += ["", "This document is confidential."]

    reader = PdfReader(io.BytesIO(_simple_pdf(lines)))
    writer = PdfWriter()
    writer.append(reader)
    writer.encrypt(user_password=password, algorithm="AES-256")
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def send_payslip(payslip, *, actor=None) -> str:
    """Email the encrypted PDF to the worker; return the one-time password
    for out-of-band delivery. The password appears nowhere else."""
    # A resend must go to the address of the last successful delivery. Person
    # details may be edited later (or a fictional demo seed may be reapplied),
    # but that must not silently change the recipient of an existing payslip.
    email = (payslip.sent_to or payslip.person.email or "").strip()
    if not email:
        raise PayslipError(_("This person has no email address on file."))

    password = generate_password()
    pdf = build_encrypted_pdf(payslip, password)

    message = EmailMessage(
        subject=_("Payslip %(period)s") % {"period": payslip.period},
        body=_(
            "Your payslip for %(period)s is attached as an encrypted PDF.\n"
            "You will receive the password separately — it is never sent by email."
        ) % {"period": payslip.period},
        to=[email],
    )
    message.attach(f"payslip-{payslip.period}.pdf", pdf, "application/pdf")
    try:
        sent = message.send(fail_silently=False)
    except (OSError, SMTPException) as exc:
        raise PayslipError(
            _("Unable to send the payslip email. Check the recipient address and mail configuration.")
        ) from exc
    if sent != 1:
        raise PayslipError(
            _("Unable to send the payslip email. Check the recipient address and mail configuration.")
        )

    payslip.sent_at = timezone.now()
    payslip.sent_to = email
    payslip.sent_by = actor if getattr(actor, "is_authenticated", False) else None
    payslip.save(update_fields=["sent_at", "sent_to", "sent_by"])
    record_event(actor, "payslip.sent", target=payslip.person, reason=payslip.period)
    return password
