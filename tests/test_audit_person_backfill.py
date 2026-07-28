"""Historical audit events must end up attributed the way new ones are.

The migration behind `AuditEvent.person` could attribute only two cases, and on
the demo database that came to **8 of 900** events. Everything a manager
actually means by "what happened to this worker?" - the equipment issue, the
room assignment, the blacklist proposal - stayed unattributed, so the person
filter still returned nothing for anyone with real history. That was the
original complaint.

These tests build events the way the seeds do, blank the attribution to
simulate a pre-migration database, and assert the command recovers it.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from django.apps import apps as django_apps
from django.core.management import call_command
from django.urls import reverse

from core.audit.models import AuditEvent
from core.audit.services import record_event
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person

if not django_apps.is_installed("features.logistics"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)

from features.compliance.models import Certificate  # noqa: E402
from features.logistics.models import (  # noqa: E402
    EquipmentIssue,
    EquipmentIssueStatus,
    EquipmentItem,
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def world(django_user_model):
    office = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    actor = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    actor.offices.set([office])
    person = Person.objects.create(
        first_name="Diana",
        last_name="Horváthová",
        office=office,
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    return {"actor": actor, "person": person, "office": office}


def _as_legacy():
    """Blank every attribution: what the table looked like before the column
    existed, and what the migration left behind for related targets."""
    AuditEvent.objects.update(person=None)


def _run(**kwargs):
    call_command("backfill_audit_persons", **kwargs)


# --- the cases the migration could not reach --------------------------------


def test_attributes_an_event_whose_target_merely_hangs_off_a_person(world):
    """`equipment.issued` targets the EquipmentIssue. This is the class of
    event the migration missed entirely."""
    item = EquipmentItem.objects.create(name="Helmet", unit_price=Decimal("30"))
    issue = EquipmentIssue.objects.create(
        person=world["person"],
        item=item,
        quantity=1,
        status=EquipmentIssueStatus.ISSUED,
    )
    event = record_event(world["actor"], "equipment.issued", target=issue)
    _as_legacy()

    _run()

    event.refresh_from_db()
    assert event.person_id == world["person"].pk


def test_attributes_a_certificate_event(world):
    certificate = Certificate.objects.create(
        person=world["person"],
        name="Medical",
        expiry_date=dt.date.today() + dt.timedelta(days=30),
    )
    event = record_event(world["actor"], "certificate.uploaded", target=certificate)
    _as_legacy()

    _run()

    event.refresh_from_db()
    assert event.person_id == world["person"].pk


def test_still_attributes_the_two_cases_the_migration_handled(world):
    """The command must not regress what already worked."""
    direct = record_event(world["actor"], "person.updated", target=world["person"])
    via_meta = record_event(
        world["actor"], "sms.sent", target=None, person=world["person"].pk
    )
    _as_legacy()

    _run()

    for event in (direct, via_meta):
        event.refresh_from_db()
        assert event.person_id == world["person"].pk


# --- the filter the client actually uses ------------------------------------


def test_the_person_filter_finds_history_after_the_backfill(client, world):
    """End to end: the complaint was that the filter returned nothing."""
    item = EquipmentItem.objects.create(name="Helmet", unit_price=Decimal("30"))
    issue = EquipmentIssue.objects.create(
        person=world["person"],
        item=item,
        quantity=1,
        status=EquipmentIssueStatus.ISSUED,
    )
    record_event(world["actor"], "equipment.issued", target=issue)
    _as_legacy()

    client.force_login(world["actor"])

    def found():
        return (
            client.get(reverse("audit_log"), {"worker": "horvat"})
            .context["page"]
            .paginator.count
        )

    assert found() == 0, "precondition: legacy rows are invisible to the filter"
    _run()
    assert found() == 1


# --- safety -----------------------------------------------------------------


def test_is_idempotent(world):
    event = record_event(world["actor"], "person.updated", target=world["person"])
    _as_legacy()

    _run()
    _run()

    event.refresh_from_db()
    assert event.person_id == world["person"].pk
    assert AuditEvent.objects.filter(person__isnull=False).count() == 1


def test_dry_run_writes_nothing(world):
    event = record_event(world["actor"], "person.updated", target=world["person"])
    _as_legacy()

    _run(dry_run=True)

    event.refresh_from_db()
    assert event.person_id is None


def test_never_reattributes_an_already_attributed_event(world):
    """Only rows with no person are considered, so a correction made by hand
    is not silently overwritten on the next run."""
    other = Person.objects.create(
        first_name="Farrukh", last_name="Tashkentov", office=world["office"]
    )
    event = record_event(world["actor"], "person.updated", target=world["person"])
    AuditEvent.objects.filter(pk=event.pk).update(person=other)

    _run()

    event.refresh_from_db()
    assert event.person_id == other.pk


def test_an_event_about_nobody_stays_unattributed(world):
    """Configuration events carry no worker's data and must not be guessed at."""
    event = record_event(world["actor"], "office.updated", target=world["office"])
    _as_legacy()

    _run()

    event.refresh_from_db()
    assert event.person_id is None


def test_a_deleted_person_is_not_resurrected_by_primary_key(world):
    """A recycled pk must not attribute an old event to a different worker."""
    event = record_event(
        world["actor"], "sms.sent", target=None, person=world["person"].pk
    )
    _as_legacy()
    world["person"].delete()

    _run()

    event.refresh_from_db()
    assert event.person_id is None
