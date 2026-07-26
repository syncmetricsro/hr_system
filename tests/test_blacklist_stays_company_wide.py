"""Blacklist must NOT be office-scoped, and that needs asserting.

Every other module gained an office boundary in ADR 0026 Phase B. Blacklist
deliberately did not (ADR 0026 point 3): a person barred at one office has to
be caught at all of them, or the control is worthless — someone rejected in
Velký Meder simply reapplies in Győr.

The risk this file guards is a *plausible* future mistake, not an unlikely
one: a sweep that adds `assert_person_in_scope` "for consistency" would look
like a security improvement in review while quietly removing fraud protection.
An absence of scoping cannot be reviewed; an assertion can.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.urls import reverse

from core.offices.models import Office
from core.people.models import LifecycleStatus, Person

if not django_apps.is_installed("features.blacklist"):
    pytest.skip("Blacklist feature not installed", allow_module_level=True)

from features.blacklist.models import BlacklistCaseStatus  # noqa: E402
from features.blacklist.services import propose_case  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def cross_office_case(django_user_model):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    vm_manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    vm_manager.offices.set([vm])
    gyor_coordinator = django_user_model.objects.create_user(
        email="coord@demo.jober.test", password="x", role="coordinator"
    )
    gyor_coordinator.offices.set([gyor])

    person = Person.objects.create(
        first_name="Farrukh",
        last_name="Gyor",
        office=gyor,
        lifecycle_status=LifecycleStatus.WORKING,
    )
    case = propose_case(person, category=None, reason="demo", actor=gyor_coordinator)
    return {"vm_manager": vm_manager, "person": person, "case": case}


def test_queue_shows_a_case_from_another_office(client, cross_office_case):
    """A Velký Meder manager must see — and be able to act on — a case raised
    in Győr. If this ever fails, fraud protection has been silently scoped."""
    client.force_login(cross_office_case["vm_manager"])
    response = client.get(reverse("blacklist_queue"))
    assert response.status_code == 200
    assert b"Farrukh" in response.content


def test_deciding_another_offices_case_is_permitted(client, cross_office_case):
    client.force_login(cross_office_case["vm_manager"])
    response = client.post(
        reverse("blacklist_decide", args=[cross_office_case["case"].pk]),
        {"decision": "approve", "reason": "confirmed"},
    )
    assert response.status_code != 403
    cross_office_case["case"].refresh_from_db()
    assert cross_office_case["case"].status != BlacklistCaseStatus.PROPOSED
