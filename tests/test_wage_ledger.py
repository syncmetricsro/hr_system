from __future__ import annotations

from decimal import Decimal

import pytest
from django.conf import settings

if "features.wage_ledger" not in settings.INSTALLED_APPS:
    pytest.skip(
        "features.wage_ledger is not installed for this client",
        allow_module_level=True,
    )

from django.core.exceptions import ValidationError  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.urls import reverse  # noqa: E402
from django.utils.translation import gettext, override  # noqa: E402

from core.audit.models import AuditEvent  # noqa: E402
from core.people.models import Person  # noqa: E402
from features.payslips.models import Payslip  # noqa: E402
from features.payslips.services import record_payslip  # noqa: E402
from features.wage_ledger.models import WageEntry  # noqa: E402
from features.wage_ledger.services import record_wage  # noqa: E402

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff(django_user_model):
    return {
        role: django_user_model.objects.create_user(
            email=f"wage-{role}@demo.corvinum.test", password="x", role=role
        )
        for role in ("manager", "observer", "coordinator", "recruiter")
    }


@pytest.fixture
def person():
    return Person.objects.create(first_name="Fictional", last_name="Worker")


def test_record_wage_is_positive_unique_and_audited(person, staff):
    entry = record_wage(
        person,
        period="2026-07",
        gross_amount=Decimal("2050.00"),
        actor=staff["manager"],
    )
    assert entry.created_by == staff["manager"]
    event = AuditEvent.objects.get(action="wage.recorded")
    assert event.target_type == "WageEntry"
    assert event.metadata["gross_amount"] == "2050.00"

    for invalid in (Decimal("0"), Decimal("-1"), "not-money"):
        with pytest.raises(ValidationError):
            record_wage(person, period="2026-06", gross_amount=invalid)

    with pytest.raises(ValidationError):
        record_wage(person, period="2026-07", gross_amount=Decimal("1.00"))


def test_wage_page_permissions_are_server_enforced(client, person, staff):
    record_wage(person, period="2026-07", gross_amount="2050", actor=staff["manager"])

    client.force_login(staff["manager"])
    assert client.get(reverse("wage_list")).status_code == 200
    assert client.post(reverse("wage_record"), {}).status_code == 400

    client.force_login(staff["observer"])
    observer = client.get(reverse("wage_list"))
    assert observer.status_code == 200
    assert reverse("wage_record").encode() not in observer.content
    assert client.post(reverse("wage_record"), {}).status_code == 403

    for role in ("coordinator", "recruiter"):
        client.force_login(staff[role])
        assert client.get(reverse("wage_list")).status_code == 403


def test_person_overview_aligns_independent_sources_without_computing_net(
    client, person, staff
):
    record_wage(person, period="2026-07", gross_amount="2050", actor=staff["manager"])
    record_payslip(person, period="2026-07", net_amount="1540", actor=staff["manager"])
    record_wage(person, period="2026-06", gross_amount="1920", actor=staff["manager"])
    client.force_login(staff["manager"])

    response = client.get(reverse("person_detail", args=[person.pk]))
    body = response.content.decode()
    assert response.status_code == 200
    with override(response.headers["Content-Language"]):
        assert gettext("Recorded gross wage") in body
        assert gettext("Recorded net payslip") in body
        assert gettext(
            "Both columns are recorded source values for the same calendar month. "
            "Gross wage is not converted into net pay here; taxes, levies, and "
            "other statutory payroll calculations remain outside this feature."
        ) in body
    rows = response.context["person_finance_overview"]["rows"]
    assert rows == [
        {
            "period": "2026-07",
            "cells": [
                {"amount": Decimal("2050.00"), "currency": "EUR"},
                {"amount": Decimal("1540.00"), "currency": "EUR"},
            ],
        },
        {
            "period": "2026-06",
            "cells": [
                {"amount": Decimal("1920.00"), "currency": "EUR"},
                None,
            ],
        },
    ]
    assert "finance-delta-mismatch" not in body


def test_observer_reads_both_sources_but_cannot_manage_payslips(client, person, staff):
    record_wage(person, period="2026-07", gross_amount="2050", actor=staff["manager"])
    record_payslip(person, period="2026-07", net_amount="1540", actor=staff["manager"])
    client.force_login(staff["observer"])

    detail = client.get(reverse("person_detail", args=[person.pk]))
    cells = detail.context["person_finance_overview"]["rows"][0]["cells"]
    assert [cell["amount"] for cell in cells] == [
        Decimal("2050.00"),
        Decimal("1540.00"),
    ]
    listing = client.get(reverse("payslip_list"))
    assert listing.status_code == 200
    assert b'name="net_amount"' not in listing.content
    assert b"/send/" not in listing.content
    assert client.post(reverse("payslip_list"), {}).status_code == 403


def test_corvinum_demo_pay_sources_are_exact_and_idempotent():
    call_command("seed_corvinum_demo", verbosity=0)
    call_command("seed_corvinum_demo", verbosity=0)
    worker = Person.objects.get(first_name="Eszter", last_name="Varga")
    assert list(
        WageEntry.objects.filter(person=worker).values_list("period", "gross_amount")
    ) == [
        ("2026-07", Decimal("2050.00")),
        ("2026-06", Decimal("1920.00")),
    ]
    assert list(
        Payslip.objects.filter(person=worker).values_list("period", "net_amount")
    ) == [
        ("2026-07", Decimal("1540.00")),
        ("2026-06", Decimal("1450.00")),
    ]
