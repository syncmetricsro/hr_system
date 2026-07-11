from __future__ import annotations

import io
import re
from decimal import Decimal

import pytest
from django.core import mail

from core.audit.models import AuditEvent
from core.people.models import Person
from features.payslips.models import Payslip
from features.payslips.services import (
    PASSWORD_ALPHABET,
    PayslipError,
    build_encrypted_pdf,
    generate_password,
    send_payslip,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="ps-manager@demo.jober.test", password="x", role="manager"
    )


@pytest.fixture
def payslip():
    person = Person.objects.create(
        first_name="Pay", last_name="Worker", email="pay.worker@demo.corvinum.test"
    )
    return Payslip.objects.create(person=person, period="2026-07", net_amount=Decimal("850.00"))


def test_password_format_and_alphabet():
    seen = set()
    for _ in range(50):
        pw = generate_password()
        assert re.fullmatch(r"[^-]{4}-[^-]{4}-[^-]{4}", pw)
        assert all(c in PASSWORD_ALPHABET for c in pw.replace("-", ""))
        assert not set("0O1lI") & set(pw)
        seen.add(pw)
    assert len(seen) == 50  # truly random, no repeats in a small sample


def test_pdf_is_aes_encrypted_and_round_trips(payslip):
    from pypdf import PdfReader
    from pypdf.errors import FileNotDecryptedError

    password = generate_password()
    data = build_encrypted_pdf(payslip, password)

    reader = PdfReader(io.BytesIO(data))
    assert reader.is_encrypted
    with pytest.raises(FileNotDecryptedError):
        reader.pages[0].extract_text()

    reader = PdfReader(io.BytesIO(data), password=password)
    text = reader.pages[0].extract_text()
    assert "850.00" in text and "2026-07" in text

    with pytest.raises(Exception):
        PdfReader(io.BytesIO(data), password="wrong-password").pages[0].extract_text()


def test_send_emails_pdf_but_never_the_password(settings, payslip, manager):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    password = send_payslip(payslip, actor=manager)

    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.to == ["pay.worker@demo.corvinum.test"]
    assert password not in message.body and password not in message.subject
    name, content, mimetype = message.attachments[0]
    assert name == "payslip-2026-07.pdf" and mimetype == "application/pdf"

    payslip.refresh_from_db()
    assert payslip.sent_at is not None and payslip.sent_to == message.to[0]
    event = AuditEvent.objects.get(action="payslip.sent")
    assert password not in (event.reason or "")


def test_send_requires_email_on_file(settings, manager):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    person = Person.objects.create(first_name="No", last_name="Email")
    slip = Payslip.objects.create(person=person, period="2026-07", net_amount=Decimal("500"))
    with pytest.raises(PayslipError):
        send_payslip(slip, actor=manager)
    assert mail.outbox == []


def test_period_uniqueness_per_person(payslip):
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        Payslip.objects.create(
            person=payslip.person, period="2026-07", net_amount=Decimal("1.00")
        )
