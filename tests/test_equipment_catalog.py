from __future__ import annotations

import pytest
from django.urls import reverse

from core.audit.models import AuditEvent
from core.people.models import Person
from features.logistics.models import EquipmentItem
from features.logistics.services import LogisticsWorkflowError, issue_equipment


pytestmark = pytest.mark.django_db


@pytest.fixture
def users(django_user_model):
    return {
        role: django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )
        for role in ("manager", "coordinator")
    }


def test_manager_can_create_search_edit_and_deactivate_equipment(client, users):
    client.force_login(users["manager"])

    created = client.post(
        reverse("equipment_create"),
        {"name": "High-visibility vest", "size": "L", "unit_price": "8.50", "is_active": "on"},
    )
    assert created.status_code == 302
    item = EquipmentItem.objects.get(name="High-visibility vest", size="L")
    assert str(item.unit_price) == "8.50"
    assert AuditEvent.objects.filter(action="equipment.catalog_created", target_id=str(item.pk)).exists()

    listing = client.get(reverse("equipment_catalog"), {"q": "vest", "status": "active"})
    assert listing.status_code == 200
    assert list(listing.context["items"]) == [item]

    updated = client.post(
        reverse("equipment_edit", args=[item.pk]),
        {"name": "High-visibility vest", "size": "L", "unit_price": "9.00"},
    )
    assert updated.status_code == 302
    item.refresh_from_db()
    assert item.is_active is False
    assert str(item.unit_price) == "9.00"
    assert AuditEvent.objects.filter(action="equipment.catalog_updated", target_id=str(item.pk)).exists()

    inactive = client.get(reverse("equipment_catalog"), {"status": "inactive"})
    assert list(inactive.context["items"]) == [item]


@pytest.mark.parametrize("url_name", ("equipment_catalog", "equipment_create"))
def test_coordinator_cannot_manage_equipment_catalog(client, users, url_name):
    client.force_login(users["coordinator"])
    assert client.get(reverse(url_name)).status_code == 403


def test_inactive_catalog_item_cannot_be_issued(users):
    item = EquipmentItem.objects.create(name="Retired boots", is_active=False)
    person = Person.objects.create(first_name="Olena", last_name="Demo")
    with pytest.raises(LogisticsWorkflowError):
        issue_equipment(person, item, actor=users["coordinator"])
