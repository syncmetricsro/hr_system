from __future__ import annotations

import io
import re
from datetime import date, datetime, timezone as datetime_timezone
from importlib import import_module
from smtplib import SMTPRecipientsRefused
from decimal import Decimal

import pytest
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage
from django.urls import reverse

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
payslip_ui = pytest.mark.skipif(
    not settings.FEATURE_FLAGS.get("payslips", False),
    reason="Payslip UI is not mounted for this client",
)


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="ps-manager@demo.jober.test", password="x", role="manager"
    )


@pytest.fixture
def observer(django_user_model):
    return django_user_model.objects.create_user(
        email="ps-observer@demo.jober.test", password="x", role="observer"
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


def test_resend_uses_the_previous_successful_delivery_address(settings, payslip, manager):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    payslip.sent_to = "controlled-demo-inbox@example.test"
    payslip.save(update_fields=["sent_to"])
    payslip.person.email = "seed-only@demo.corvinum.test"
    payslip.person.save(update_fields=["email"])

    send_payslip(payslip, actor=manager)

    assert mail.outbox[0].to == ["controlled-demo-inbox@example.test"]


def test_smtp_recipient_failure_becomes_a_safe_payslip_error(monkeypatch, payslip, manager):
    def reject(*_args, **_kwargs):
        raise SMTPRecipientsRefused({"bad@example.test": (550, b"invalid recipient")})

    monkeypatch.setattr(EmailMessage, "send", reject)
    with pytest.raises(PayslipError) as excinfo:
        send_payslip(payslip, actor=manager)

    assert "bad@example.test" not in str(excinfo.value)

    payslip.refresh_from_db()
    assert payslip.sent_at is None and payslip.sent_to == ""


def test_record_payslip_is_audited(manager):
    from features.payslips.services import record_payslip

    person = Person.objects.create(first_name="Audit", last_name="Trail")
    slip = record_payslip(
        person,
        period="2026-07",
        net_amount="900.00",
        issue_date=date(2026, 8, 4),
        actor=manager,
    )
    event = AuditEvent.objects.get(action="payslip.recorded")
    assert all(value in event.reason for value in ("2026-07", "900.00", "2026-08-04"))
    assert event.metadata == {
        "issue_date": "2026-08-04",
        "period": "2026-07",
        "net_amount": "900.00",
        "currency": "EUR",
    }
    assert slip.created_by == manager


def test_record_payslip_defaults_issue_date_to_local_creation_date(manager, monkeypatch):
    from features.payslips import services

    person = Person.objects.create(first_name="Default", last_name="Date")
    expected = date(2026, 7, 21)
    monkeypatch.setattr(services.timezone, "localdate", lambda: expected)

    slip = services.record_payslip(
        person, period="2026-07", net_amount="901.00", actor=manager
    )

    assert slip.issue_date == expected


def test_issue_date_backfill_uses_bratislava_local_date(settings):
    settings.TIME_ZONE = "Europe/Bratislava"
    migration = import_module("features.payslips.migrations.0002_payslip_issue_date")
    late_utc = datetime(2026, 7, 20, 22, 30, tzinfo=datetime_timezone.utc)

    assert migration.local_issue_date(late_utc) == date(2026, 7, 21)


@payslip_ui
def test_payslip_form_accepts_blank_and_future_issue_dates(client, manager, monkeypatch):
    from features.payslips import services

    person = Person.objects.create(first_name="Form", last_name="Worker")
    client.force_login(manager)
    expected_default = date(2026, 7, 21)
    monkeypatch.setattr(services.timezone, "localdate", lambda: expected_default)

    blank = client.post(
        reverse("payslip_list"),
        {"person": person.pk, "period": "2026-07", "net_amount": "700", "issue_date": ""},
    )
    assert blank.status_code == 302
    assert Payslip.objects.get(person=person, period="2026-07").issue_date == expected_default

    future = client.post(
        reverse("payslip_list"),
        {
            "person": person.pk,
            "period": "2026-08",
            "net_amount": "710",
            "issue_date": "2099-01-02",
        },
    )
    assert future.status_code == 302
    assert Payslip.objects.get(person=person, period="2026-08").issue_date == date(2099, 1, 2)


@payslip_ui
def test_invalid_issue_date_rerenders_bound_form(client, manager):
    person = Person.objects.create(first_name="Invalid", last_name="Date")
    client.force_login(manager)

    response = client.post(
        reverse("payslip_list"),
        {
            "person": person.pk,
            "period": "2026-07",
            "net_amount": "700",
            "issue_date": "not-a-date",
        },
    )

    assert response.status_code == 400
    assert b'name="issue_date"' in response.content
    assert not Payslip.objects.filter(person=person).exists()


@payslip_ui
def test_issue_date_is_visible_in_list_to_manager_and_observer(
    client, payslip, manager, observer
):
    payslip.issue_date = date(2026, 8, 3)
    payslip.save(update_fields=["issue_date"])

    for user in (manager, observer):
        client.force_login(user)
        response = client.get(reverse("payslip_list"))
        assert response.status_code == 200
        assert b"2026-08-03" in response.content
        assert b'data-table-scroll' in response.content

    assert b'name="issue_date"' not in response.content


def test_period_uniqueness_per_person(payslip):
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        Payslip.objects.create(
            person=payslip.person, period="2026-07", net_amount=Decimal("1.00")
        )
