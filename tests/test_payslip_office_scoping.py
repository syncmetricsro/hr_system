"""Payslips must honour the office boundary (ADR 0026).

Recorded as a known gap while the recipient allowlist was being built and left
open on the grounds that it was not exploitable: CorvinumEU creates no `Office`
rows, so `user_office_scope` returns its unrestricted sentinel, and Jober has
payslips switched off. Both halves of that are configuration, and configuration
changes.

Three separate leaks, not one. The send view took a pk with no guard, so a
manager could email another office's worker their payslip - and that POST also
mints and displays a one-time password, so it leaked more than the document.
The list showed every office's net pay, which is restricted data:
`PAYSLIP_VIEW` sits in the *sensitive reads* group of the `Action` enum. And
the record form's person dropdown offered every worker in the company, so a
payslip could be created against someone out of scope in the first place.

Deliberately not `jober_only`: `features.payslips` is installed for both
clients, and the corvinum lane is where the feature is actually mounted.
Request-level through `client`, because what was missing was the *call* to a
guard that already existed and was already correct.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.conf import settings as django_settings
from django.core import mail
from django.urls import reverse

from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from features.payslips.forms import PayslipForm
from features.payslips.models import Payslip

pytestmark = pytest.mark.django_db

payslip_ui = pytest.mark.skipif(
    not django_settings.FEATURE_FLAGS.get("payslips", False),
    reason="Payslip UI is not mounted for this client",
)


@pytest.fixture(autouse=True)
def _locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.EMAIL_ALLOWED_RECIPIENTS = []
    mail.outbox.clear()
    return settings


@pytest.fixture
def two_offices(django_user_model):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="ps-scope-mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([vm])
    superuser = django_user_model.objects.create_superuser(
        email="ps-scope-root@demo.jober.test", password="x"
    )

    mine = Person.objects.create(
        first_name="Olha",
        last_name="VM",
        office=vm,
        email="olha@demo.corvinum.test",
        lifecycle_status=LifecycleStatus.WORKING,
    )
    theirs = Person.objects.create(
        first_name="Farrukh",
        last_name="Gyor",
        office=gyor,
        email="farrukh@demo.corvinum.test",
        lifecycle_status=LifecycleStatus.WORKING,
    )
    return {
        "vm": vm,
        "gyor": gyor,
        "manager": manager,
        "superuser": superuser,
        "mine": mine,
        "theirs": theirs,
        "my_slip": Payslip.objects.create(
            person=mine, period="2026-07", net_amount=Decimal("1450.00")
        ),
        "their_slip": Payslip.objects.create(
            person=theirs, period="2026-07", net_amount=Decimal("1540.00")
        ),
    }


# --- sending ---------------------------------------------------------------


@payslip_ui
def test_sending_another_offices_payslip_is_forbidden(client, two_offices):
    client.force_login(two_offices["manager"])

    response = client.post(reverse("payslip_send", args=[two_offices["their_slip"].pk]))

    assert response.status_code == 403
    assert mail.outbox == []
    two_offices["their_slip"].refresh_from_db()
    assert two_offices["their_slip"].sent_at is None


@payslip_ui
def test_sending_within_own_office_is_allowed(client, two_offices):
    """The guard rejects the *other* office, not everything — one account
    seeing less proves nothing on its own."""
    client.force_login(two_offices["manager"])

    response = client.post(reverse("payslip_send", args=[two_offices["my_slip"].pk]))

    assert response.status_code == 302
    assert len(mail.outbox) == 1
    two_offices["my_slip"].refresh_from_db()
    assert two_offices["my_slip"].sent_at is not None


@payslip_ui
def test_a_blocked_send_mints_no_password(client, two_offices, monkeypatch):
    """The success path shows a one-time password in a flash message, so an
    unguarded cross-office POST would have leaked a credential as well as the
    document. Nothing may be generated before the boundary check."""

    def explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("a payslip PDF was built for another office")

    monkeypatch.setattr("features.payslips.services.build_encrypted_pdf", explode)
    client.force_login(two_offices["manager"])

    assert (
        client.post(
            reverse("payslip_send", args=[two_offices["their_slip"].pk])
        ).status_code
        == 403
    )


@payslip_ui
def test_an_unrestricted_role_is_not_blocked(client, two_offices):
    client.force_login(two_offices["superuser"])

    response = client.post(reverse("payslip_send", args=[two_offices["their_slip"].pk]))

    assert response.status_code == 302


# --- the list --------------------------------------------------------------


@payslip_ui
def test_the_list_shows_only_my_offices_pay_data(client, two_offices):
    """Net pay is a sensitive read, so a cross-office row is a data leak even
    though nothing is written."""
    client.force_login(two_offices["manager"])

    response = client.get(reverse("payslip_list"))

    listed = {slip.person for slip in response.context["payslips"]}
    assert listed == {two_offices["mine"]}


@payslip_ui
def test_an_unrestricted_role_sees_every_office(client, two_offices):
    client.force_login(two_offices["superuser"])

    response = client.get(reverse("payslip_list"))

    listed = {slip.person for slip in response.context["payslips"]}
    assert listed == {two_offices["mine"], two_offices["theirs"]}


# --- the record form -------------------------------------------------------


def test_the_person_picker_is_scoped(two_offices):
    form = PayslipForm(user=two_offices["manager"])
    assert list(form.fields["person"].queryset) == [two_offices["mine"]]


def test_the_person_picker_is_unrestricted_for_a_superuser(two_offices):
    form = PayslipForm(user=two_offices["superuser"])
    assert set(form.fields["person"].queryset) == {
        two_offices["mine"],
        two_offices["theirs"],
    }


def test_recording_against_another_office_is_rejected(two_offices):
    """The queryset is the validation: a hand-crafted POST naming an
    out-of-scope person fails `is_valid()` rather than silently creating."""
    form = PayslipForm(
        {
            "person": two_offices["theirs"].pk,
            "period": "2026-08",
            "net_amount": "1000.00",
            "note": "",
        },
        user=two_offices["manager"],
    )

    assert not form.is_valid()
    assert "person" in form.errors


def test_no_user_means_no_scoping(two_offices):
    """Management commands and seeds build the form without a request."""
    form = PayslipForm()
    assert set(form.fields["person"].queryset) == {
        two_offices["mine"],
        two_offices["theirs"],
    }
