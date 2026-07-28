"""Jober never takes issued equipment back (J6).

The client was unambiguous: "what we issue, stays out". Removing the path is
per-client, not global - CorvinumEU keeps return-to-stock, the manager recovery
review and the linked ledger deduction.

Done the way the transport removal was: the route is simply not registered for
a client whose flag is off, and models and migrations are preserved untouched
so history stays readable. Nothing is deleted.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.urls import NoReverseMatch, reverse

from core.ui.registry import flag_enabled

if not django_apps.is_installed("features.logistics"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)


def test_the_flag_matches_this_client():
    """Guards the flag itself, so a client settings edit that silently flips
    returns back on fails here rather than in a demo."""
    from django.conf import settings

    assert (
        flag_enabled("equipment_returns") is settings.FEATURE_FLAGS["equipment_returns"]
    )


@pytest.mark.jober_only
def test_jober_has_no_return_route_at_all():
    """Not a 403 - the URL does not exist, the same way transport's did not
    after it was retired. A route that 403s is still a route to maintain."""
    with pytest.raises(NoReverseMatch):
        reverse("return_equipment", args=[1])


@pytest.mark.jober_only
def test_jober_still_issues_equipment():
    """Guard the opposite failure: removing returns must not remove issuing."""
    assert reverse("issue_equipment", args=[1])


@pytest.mark.jober_only
def test_jober_keeps_the_stock_correction_path():
    """With returns gone, manual adjustment is the only way to put quantity
    back - the client approved it and it must survive."""
    assert reverse("equipment_stock_adjust")


@pytest.mark.jober_only
@pytest.mark.django_db
def test_the_return_form_is_not_rendered(client, django_user_model):
    """The route being gone is not enough if a template still links it: the
    page would raise NoReverseMatch rather than simply omitting the button."""
    from decimal import Decimal

    from core.people.models import Person
    from features.logistics.models import (
        EquipmentIssue,
        EquipmentIssueStatus,
        EquipmentItem,
    )

    person = Person.objects.create(first_name="Demo", last_name="Worker")
    item = EquipmentItem.objects.create(name="Helmet", unit_price=Decimal("30"))
    EquipmentIssue.objects.create(
        person=person, item=item, quantity=1, status=EquipmentIssueStatus.ISSUED
    )
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)

    response = client.get(reverse("person_detail", args=[person.pk]))
    body = response.content.decode()
    assert response.status_code == 200
    assert "Reusable" not in body
    assert "/return/" not in body


@pytest.mark.jober_only
@pytest.mark.django_db
def test_history_is_preserved_not_deleted(django_user_model):
    """Previously returned items must still be readable. The models and their
    migrations are untouched; only the path forward is closed."""
    from decimal import Decimal

    from core.people.models import Person
    from features.logistics.models import (
        EquipmentIssue,
        EquipmentIssueStatus,
        EquipmentItem,
    )

    person = Person.objects.create(first_name="Demo", last_name="Worker")
    item = EquipmentItem.objects.create(name="Vest", unit_price=Decimal("8"))
    returned = EquipmentIssue.objects.create(
        person=person,
        item=item,
        quantity=1,
        status=EquipmentIssueStatus.RETURNED,
    )
    assert EquipmentIssue.objects.filter(pk=returned.pk).exists()
    assert returned.get_status_display()


def test_a_client_that_keeps_returns_still_has_the_route():
    """The mirror of the Jober test, and the one that matters for CorvinumEU:
    this removal is per-client, and a global one would satisfy every Jober
    assertion above while silently breaking the other client."""
    if not flag_enabled("equipment_returns"):
        pytest.skip("this client has returns disabled")
    assert reverse("return_equipment", args=[1])
