"""The audit person filter must find everything about a worker, and stay inside
the office boundary.

The client reported it as "returns no rows". Reproducing it showed something
narrower and more interesting: it matched `target_type="Person"`, so it found
only events whose *target row* was the person. A certificate upload targets the
Certificate; an equipment issue targets the EquipmentIssue. Both are events
about a worker, and neither was findable — so a manager asking "what happened
to Diana?" saw a fraction of the answer and reasonably concluded it was broken.

Two further things this covers:

* **Diacritics.** `search_name` stored "horváthová" verbatim, so typing
  "horvat" — which is what people actually do — matched nothing. Slovak and
  Hungarian names carry accents that are routinely omitted at the keyboard.
* **Office scoping.** The audit log had *none*. A Velký Meder manager could
  read every action taken on Győr and Dunajská Streda workers. The fix scopes
  attributed events and deliberately leaves unattributed ones visible; that
  choice is asserted below so it cannot drift silently.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.apps import apps as django_apps
from django.urls import reverse

from core.audit.models import AuditEvent
from core.audit.services import record_event
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person

if not django_apps.is_installed("features.compliance"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)

from features.compliance.models import Certificate  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def world(django_user_model):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([vm])
    observer = django_user_model.objects.create_user(
        email="obs@demo.jober.test", password="x", role="observer"
    )

    diana = Person.objects.create(
        first_name="Diana",
        last_name="Horváthová",
        office=vm,
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    farrukh = Person.objects.create(
        first_name="Farrukh",
        last_name="Tashkentov",
        office=gyor,
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    return {
        "manager": manager,
        "observer": observer,
        "diana": diana,
        "farrukh": farrukh,
    }


def _count(client, **params) -> int:
    return client.get(reverse("audit_log"), params).context["page"].paginator.count


# --- events about a person, not merely targeting one -----------------------


def test_finds_events_whose_target_is_not_the_person(client, world):
    """The actual defect. A certificate event targets the Certificate, so the
    old target_type="Person" filter could never find it."""
    diana = world["diana"]
    certificate = Certificate.objects.create(
        person=diana,
        name="Medical",
        expiry_date=dt.date.today() + dt.timedelta(days=30),
    )
    record_event(world["manager"], "person.updated", target=diana)
    record_event(world["manager"], "certificate.uploaded", target=certificate)

    client.force_login(world["manager"])
    assert _count(client, worker="Diana") == 2


def test_person_kwarg_also_attributes(client, world):
    """Several call sites already passed person=<pk> as metadata; honour it."""
    record_event(world["manager"], "sms.sent", target=None, person=world["diana"].pk)
    client.force_login(world["manager"])
    assert _count(client, worker="Diana") == 1


# --- diacritics ------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [
        "Diana",
        "diana",
        "DIANA",
        "horvat",
        "Horvat",
        "horváth",
        "Horváthová",
        "diana horvat",
    ],
)
def test_name_matching_is_case_and_diacritic_insensitive(client, world, query):
    record_event(world["manager"], "person.updated", target=world["diana"])
    client.force_login(world["manager"])
    assert _count(client, worker=query) == 1, f"{query!r} found nothing"


def test_a_non_matching_name_still_returns_nothing(client, world):
    """Guard the opposite error: folding must not make everything match."""
    record_event(world["manager"], "person.updated", target=world["diana"])
    client.force_login(world["manager"])
    assert _count(client, worker="Kovac") == 0


# --- office scoping (ADR 0026), which the log had none of ------------------


def test_manager_cannot_see_another_offices_worker_events(client, world):
    record_event(world["manager"], "person.updated", target=world["farrukh"])
    client.force_login(world["manager"])
    assert _count(client, worker="Farrukh") == 0


def test_observer_sees_every_office(client, world):
    record_event(world["manager"], "person.updated", target=world["farrukh"])
    client.force_login(world["observer"])
    assert _count(client, worker="Farrukh") == 1


def test_unattributed_events_stay_visible(client, world):
    """The documented decision: events with no person are configuration and
    system actions carrying no worker's data, so scoping them away would blind
    a manager to their own app's history for no privacy gain."""
    record_event(world["manager"], "catalog.updated", target=None)
    client.force_login(world["manager"])
    total = _count(client)
    assert total == 1


def test_scoping_and_the_person_filter_compose(client, world):
    """Both filters at once — the composition case the client hit."""
    record_event(world["manager"], "person.updated", target=world["diana"])
    record_event(world["manager"], "person.updated", target=world["farrukh"])
    client.force_login(world["manager"])
    assert _count(client) == 1  # scoping alone
    assert _count(client, worker="Diana") == 1  # scoping + person
    assert _count(client, worker="Farrukh") == 0  # scoping wins


# --- attribution should not break anything ---------------------------------


def test_recording_an_event_never_fails_on_an_unresolvable_target(world):
    """Audit writes sit inside business transactions. Attribution is
    best-effort by design: a target with no person must not raise."""
    event = record_event(
        world["manager"], "office.updated", target=Office.objects.first()
    )
    assert event.person is None
    assert AuditEvent.objects.filter(pk=event.pk).exists()
