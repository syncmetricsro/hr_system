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
from django.test import RequestFactory, override_settings  # noqa: E402
from django.urls import reverse  # noqa: E402
from django.utils.translation import gettext, override  # noqa: E402

from core.audit.models import AuditEvent  # noqa: E402
from core.people.models import Person  # noqa: E402
from core.ui.registry import person_finance_overview  # noqa: E402
from features.payslips.models import Payslip  # noqa: E402
from features.payslips.providers import net_payslip_series  # noqa: E402
from features.wage_ledger.models import WageEntry  # noqa: E402
from features.wage_ledger.providers import gross_wage_series  # noqa: E402
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
        gross_amount=Decimal("1200.00"),
        actor=staff["manager"],
    )
    assert entry.created_by == staff["manager"]
    event = AuditEvent.objects.get(action="wage.recorded")
    assert event.target_type == "WageEntry"
    assert event.target_id == str(entry.pk)
    assert event.metadata["person_id"] == person.pk
    assert event.metadata["gross_amount"] == "1200.00"

    for invalid in (Decimal("0"), Decimal("-1"), "not-money"):
        with pytest.raises(ValidationError):
            record_wage(person, period="2026-06", gross_amount=invalid)

    with pytest.raises(ValidationError):
        record_wage(person, period="2026-07", gross_amount=Decimal("1.00"))


def test_wage_page_is_read_only_for_observer(client, person, staff):
    record_wage(person, period="2026-07", gross_amount="1200", actor=staff["manager"])

    client.force_login(staff["manager"])
    manager_response = client.get(reverse("wage_list"))
    assert manager_response.status_code == 200
    assert reverse("wage_record").encode() in manager_response.content

    client.force_login(staff["observer"])
    observer_response = client.get(reverse("wage_list"))
    assert observer_response.status_code == 200
    assert reverse("wage_record").encode() not in observer_response.content
    assert client.post(reverse("wage_record"), {}).status_code == 403

    for role in ("coordinator", "recruiter"):
        client.force_login(staff[role])
        assert client.get(reverse("wage_list")).status_code == 403


def test_wage_form_rejects_duplicate_person_period(client, person, staff):
    record_wage(person, period="2026-07", gross_amount="1200", actor=staff["manager"])
    client.force_login(staff["manager"])
    response = client.post(
        reverse("wage_record"),
        {
            "person": person.pk,
            "period": "2026-07",
            "gross_amount": "1300.00",
            "note": "duplicate",
        },
    )
    assert response.status_code == 400
    assert WageEntry.objects.filter(person=person, period="2026-07").count() == 1


def test_person_overview_aligns_gross_wage_and_net_payslip(client, person, staff):
    record_wage(person, period="2026-07", gross_amount="1200", actor=staff["manager"])
    Payslip.objects.create(person=person, period="2026-07", net_amount="900")
    client.force_login(staff["manager"])

    response = client.get(reverse("person_detail", args=[person.pk]))
    assert response.status_code == 200
    language = response.headers["Content-Language"]
    with override(language):
        assert gettext("Gross wage").encode() in response.content
        assert gettext("Net payslip").encode() in response.content
    assert b"2026-07" in response.content
    assert b"1200" in response.content
    assert b"900" in response.content


def test_finance_series_honor_flag_and_permission(person, staff):
    record_wage(person, period="2026-07", gross_amount="1200", actor=staff["manager"])
    Payslip.objects.create(person=person, period="2026-07", net_amount="900")
    request = RequestFactory().get("/")

    request.user = staff["coordinator"]
    assert gross_wage_series(request, person) is None
    assert net_payslip_series(request, person) is None

    request.user = staff["observer"]
    assert gross_wage_series(request, person) is not None
    assert net_payslip_series(request, person) is not None
    overview = person_finance_overview(request, person)
    assert overview is not None
    assert [series["label"] for series in overview["series"]] == [
        gettext("Gross wage"),
        gettext("Net payslip"),
    ]

    flags = {**settings.FEATURE_FLAGS, "wage_ledger": False, "payslips": False}
    with override_settings(FEATURE_FLAGS=flags):
        assert gross_wage_series(request, person) is None
        assert net_payslip_series(request, person) is None


def test_corvinum_demo_wage_and_payslip_seed_is_idempotent():
    call_command("seed_corvinum_demo", verbosity=0)
    call_command("seed_corvinum_demo", verbosity=0)
    worker = Person.objects.get(first_name="Marek", last_name="Skladník")
    assert list(
        WageEntry.objects.filter(person=worker).values_list("period", flat=True)
    ) == ["2026-07", "2026-06"]
    assert list(
        Payslip.objects.filter(person=worker).values_list("period", flat=True)
    ) == ["2026-07", "2026-06"]
