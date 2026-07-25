from __future__ import annotations

import pytest
from django.urls import reverse

from core.audit.services import record_event
from core.offices.models import Office
from core.people.models import Person
from core.projects.models import Project, ReadinessRecord, TrialAssignment
from core.ui.registry import flag_enabled
from features.checklists.models import (
    ChecklistItemTemplate,
    ChecklistTemplate,
    PersonChecklistItem,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def two_offices(django_user_model):
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    observer = django_user_model.objects.create_user(
        email="obs@demo.jober.test", password="x", role="observer"
    )

    p_vm = Project.objects.create(name="VM Project", code="VMPROJ", office=velky_meder)
    p_gyr = Project.objects.create(name="Győr Project", code="GYRPROJ", office=gyor)
    return {
        "velky_meder": velky_meder,
        "gyor": gyor,
        "manager": manager,
        "observer": observer,
        "p_vm": p_vm,
        "p_gyr": p_gyr,
    }


def test_routine_update_hidden_for_other_offices_record(client, two_offices):
    vm_person = Person.objects.create(
        first_name="Olha", last_name="VM", office=two_offices["velky_meder"]
    )
    gyr_person = Person.objects.create(
        first_name="Farrukh", last_name="Gyor", office=two_offices["gyor"]
    )
    client.force_login(two_offices["manager"])
    client.get(reverse("notification_panel"))  # establishes session baseline

    actor = two_offices["observer"]
    record_event(actor, "person.updated", target=vm_person)
    record_event(actor, "person.updated", target=gyr_person)

    updates = client.get(reverse("notification_panel")).context["notification_center"][
        "updates"
    ]
    subjects = {item.detail for item in updates}
    assert any("Olha" in s for s in subjects)
    assert not any("Farrukh" in s for s in subjects)


def test_routine_update_for_an_office_less_person_follows_ownership(
    client, two_offices, django_user_model
):
    """Superseded the original fail-open assertion here (2026-07-25): an
    office-less person is their owning recruiter's to see, not everyone's, so
    this feed follows the same rule as the person views rather than keeping a
    second, looser definition."""
    recruiter = django_user_model.objects.create_user(
        email="rec@demo.jober.test", password="x", role="recruiter"
    )
    recruiter.offices.set([two_offices["velky_meder"]])
    unassigned = Person.objects.create(
        first_name="Unassigned", last_name="Candidate", owning_recruiter=recruiter
    )

    # The manager does not own them, so the update stays out of their feed.
    client.force_login(two_offices["manager"])
    client.get(reverse("notification_panel"))
    record_event(two_offices["observer"], "person.updated", target=unassigned)
    updates = client.get(reverse("notification_panel")).context["notification_center"][
        "updates"
    ]
    assert not any("Unassigned" in item.detail for item in updates)

    # The owning recruiter does see it.
    client.force_login(recruiter)
    client.get(reverse("notification_panel"))
    record_event(two_offices["observer"], "person.updated", target=unassigned)
    updates = client.get(reverse("notification_panel")).context["notification_center"][
        "updates"
    ]
    assert any("Unassigned" in item.detail for item in updates)


def test_core_alert_trial_outcome_scoped_to_manager_office(client, two_offices):
    vm_person = Person.objects.create(first_name="Olha", last_name="VM")
    gyr_person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    vm_trial = TrialAssignment.objects.create(
        person=vm_person, project=two_offices["p_vm"]
    )
    TrialAssignment.objects.create(person=gyr_person, project=two_offices["p_gyr"])

    client.force_login(two_offices["manager"])
    alerts = client.get(reverse("notification_panel")).context["notification_center"][
        "alerts"
    ]
    keys = [item.key for item in alerts if item.key.startswith("trial-outcome:")]
    assert keys == [f"trial-outcome:{vm_trial.pk}"]


def test_core_alert_readiness_scoped_to_manager_office(client, two_offices):
    vm_person = Person.objects.create(first_name="Olha", last_name="VM")
    gyr_person = Person.objects.create(first_name="Farrukh", last_name="Gyor")
    vm_readiness = ReadinessRecord.objects.create(
        person=vm_person, project=two_offices["p_vm"]
    )
    ReadinessRecord.objects.create(person=gyr_person, project=two_offices["p_gyr"])

    client.force_login(two_offices["manager"])
    alerts = client.get(reverse("notification_panel")).context["notification_center"][
        "alerts"
    ]
    keys = [item.key for item in alerts if item.key.startswith("readiness:")]
    assert keys == [f"readiness:{vm_readiness.pk}"]


def test_checklist_notification_hides_other_offices_item(client, two_offices):
    if not flag_enabled("checklists"):
        pytest.skip("checklists is not enabled for this client")
    template = ChecklistTemplate.objects.create(name="Global activation")
    item_template = ChecklistItemTemplate.objects.create(
        template=template, label="Identity verified", critical=True, order=1
    )
    vm_person = Person.objects.create(
        first_name="Olha", last_name="VM", office=two_offices["velky_meder"]
    )
    gyr_person = Person.objects.create(
        first_name="Farrukh", last_name="Gyor", office=two_offices["gyor"]
    )
    PersonChecklistItem.objects.create(person=vm_person, item_template=item_template)
    PersonChecklistItem.objects.create(person=gyr_person, item_template=item_template)

    client.force_login(two_offices["manager"])
    alerts = client.get(reverse("notification_panel")).context["notification_center"][
        "alerts"
    ]
    checklist_details = [
        item.detail for item in alerts if item.key.startswith("checklist:")
    ]
    assert any("Olha" in d for d in checklist_details)
    assert not any("Farrukh" in d for d in checklist_details)


def test_core_alerts_unaffected_when_no_offices_exist(client, django_user_model):
    """CorvinumEU: zero Office rows anywhere - core alerts still cover
    everyone, not restricted to nothing."""
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    person = Person.objects.create(first_name="No", last_name="Office")
    project = Project.objects.create(name="No Office Project", code="NOOFF")
    trial = TrialAssignment.objects.create(person=person, project=project)

    client.force_login(manager)
    alerts = client.get(reverse("notification_panel")).context["notification_center"][
        "alerts"
    ]
    keys = [item.key for item in alerts if item.key.startswith("trial-outcome:")]
    assert keys == [f"trial-outcome:{trial.pk}"]
