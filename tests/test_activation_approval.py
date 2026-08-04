"""Activating a worker is a decision, not a status change, and it is recorded.

Before this existed, the coordinator who completed the four readiness pillars
could activate in the next click — so the person filling in the checklist was
the person approving it, and nobody ever checked the checker
(production-readiness item 14). The four-pillar gate was real; the manager
approval the design specified simply was not implemented.

"Activate" is not a status label: it is the moment the worker is deployed to a
client site, accommodation is committed, equipment is issued and billing
starts. That is why a manager decides it.

The decider used to be *required* to be someone other than the requester. An
office can have a single administrator, and that rule left them unable to
activate anyone at all — proved on CorvinumEU staging, where two requests sat
permanently undecidable. Since ADR 0031 the separation of duties is recorded
rather than enforced: a self-approval goes through and says so.
"""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.accounts.models import Role
from core.audit.models import AuditEvent
from core.offices.models import Office
from core.people.models import LifecycleStatus, Person
from core.projects.models import (
    ActivationApprovalStatus,
    PillarState,
    Project,
    TrialOutcome,
)
from core.projects.services import (
    WorkflowError,
    decide_activation,
    get_or_create_readiness,
    record_trial_outcome,
    request_activation,
    schedule_trial,
    update_readiness,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def world(django_user_model):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")

    def user(email, role, office):
        u = django_user_model.objects.create_user(email=email, password="x", role=role)
        if office:
            u.offices.set([office])
        return u

    coordinator = user("coord@demo.jober.test", Role.COORDINATOR, vm)
    manager = user("mgr@demo.jober.test", Role.MANAGER, vm)
    gyor_manager = user("mgr.gyor@demo.jober.test", Role.MANAGER, gyor)

    project = Project.objects.create(name="DHL", code="DHL", office=vm, is_active=True)
    project.responsible_coordinators.add(coordinator)
    person = Person.objects.create(
        first_name="Olha",
        last_name="K",
        office=vm,
        lifecycle_status=LifecycleStatus.AVAILABLE,
    )
    trial = schedule_trial(person, project, actor=coordinator)
    record_trial_outcome(trial, TrialOutcome.PASS, actor=coordinator)
    readiness = get_or_create_readiness(person, project)
    update_readiness(
        readiness,
        actor=coordinator,
        states={
            "medical": PillarState.COMPLETE,
            "gear": PillarState.COMPLETE,
            "accommodation": PillarState.COMPLETE,
            "transport": PillarState.NOT_APPLICABLE,
        },
        na_reasons={"transport": "own car"},
    )
    return {
        "vm": vm,
        "gyor": gyor,
        "coordinator": coordinator,
        "manager": manager,
        "gyor_manager": gyor_manager,
        "project": project,
        "person": person,
    }


# --- the control itself ----------------------------------------------------


def test_requesting_does_not_activate(world):
    """If a request activated, the second pair of eyes would be decorative."""
    request_activation(world["person"], world["project"], actor=world["coordinator"])
    world["person"].refresh_from_db()
    assert world["person"].lifecycle_status != LifecycleStatus.WORKING


def test_a_manager_approval_activates(world):
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    decide_activation(approval, "approve", actor=world["manager"])
    world["person"].refresh_from_db()
    assert world["person"].lifecycle_status == LifecycleStatus.WORKING


@pytest.mark.jober_only
def test_coordinator_cannot_reach_the_decision_endpoint(client, world):
    """The action gate. A coordinator holds readiness.complete and
    project.assign but not approval.activate."""
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    client.force_login(world["coordinator"])
    response = client.post(
        reverse("activation_decide", args=[approval.pk]), {"decision": "approve"}
    )
    assert response.status_code == 403
    world["person"].refresh_from_db()
    assert world["person"].lifecycle_status != LifecycleStatus.WORKING


@pytest.mark.jober_only
def test_a_manager_can_decide_their_own_request(client, world):
    """The single-administrator case (ADR 0031). This used to answer 403, which
    made activation impossible in an office with one manager rather than making
    it stricter."""
    approval = request_activation(
        world["person"], world["project"], actor=world["manager"]
    )
    client.force_login(world["manager"])
    response = client.post(
        reverse("activation_decide", args=[approval.pk]), {"decision": "approve"}
    )
    assert response.status_code == 302
    approval.refresh_from_db()
    assert approval.status == ActivationApprovalStatus.APPROVED
    world["person"].refresh_from_db()
    assert world["person"].lifecycle_status == LifecycleStatus.WORKING


def test_a_self_approval_says_so_in_the_audit_log(world):
    """Allowing it is only defensible if it is visible afterwards. This is the
    query an auditor asks: which activations had no second pair of eyes?"""
    approval = request_activation(
        world["person"], world["project"], actor=world["manager"]
    )
    decide_activation(approval, "approve", actor=world["manager"])

    event = AuditEvent.objects.filter(action="activation.approved").latest("id")
    assert event.metadata.get("self_approved") is True


def test_an_ordinary_approval_carries_no_self_approved_marker(world):
    """Otherwise the marker is on every row and searching for it finds nothing
    — the requester and the decider are different people here."""
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    decide_activation(approval, "approve", actor=world["manager"])

    event = AuditEvent.objects.filter(action="activation.approved").latest("id")
    assert "self_approved" not in event.metadata


# --- rejection is only useful if it says why -------------------------------


def test_rejection_requires_a_reason(world):
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    with pytest.raises(WorkflowError):
        decide_activation(approval, "reject", actor=world["manager"], reason="   ")
    approval.refresh_from_db()
    assert approval.status == ActivationApprovalStatus.PENDING


def test_rejection_leaves_the_worker_in_readiness_to_try_again(world):
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    decide_activation(
        approval, "reject", actor=world["manager"], reason="medical not on file"
    )
    world["person"].refresh_from_db()
    assert world["person"].lifecycle_status != LifecycleStatus.WORKING
    # and a fresh request is possible once the problem is fixed
    again = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    assert again.status == ActivationApprovalStatus.PENDING


def test_only_one_open_request_at_a_time(world):
    request_activation(world["person"], world["project"], actor=world["coordinator"])
    with pytest.raises(WorkflowError):
        request_activation(
            world["person"], world["project"], actor=world["coordinator"]
        )


# --- readiness can regress between request and decision --------------------


def test_approval_rechecks_readiness(world):
    """Readiness stays editable after a request. Approving a worker whose
    medical has since lapsed would defeat the gate the approval double-checks."""
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    readiness = approval.readiness
    readiness.medical_state = PillarState.INCOMPLETE
    readiness.save()
    with pytest.raises(WorkflowError):
        decide_activation(approval, "approve", actor=world["manager"])
    world["person"].refresh_from_db()
    assert world["person"].lifecycle_status != LifecycleStatus.WORKING


def test_snapshot_records_what_was_asked_for(world):
    """The manager approves what the coordinator submitted, not whatever the
    record happens to say when they open the queue."""
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    readiness = approval.readiness
    readiness.medical_state = PillarState.INCOMPLETE
    readiness.save()
    approval.refresh_from_db()
    assert approval.pillar_snapshot["medical"] == PillarState.COMPLETE


# --- office scoping (ADR 0026) ---------------------------------------------


@pytest.mark.jober_only
def test_queue_shows_only_your_offices(client, world):
    request_activation(world["person"], world["project"], actor=world["coordinator"])
    client.force_login(world["gyor_manager"])
    response = client.get(reverse("activation_queue"))
    assert response.status_code == 200
    assert b"Olha" not in response.content

    client.force_login(world["manager"])
    response = client.get(reverse("activation_queue"))
    assert b"Olha" in response.content


@pytest.mark.jober_only
def test_deciding_another_offices_request_is_forbidden(client, world):
    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    client.force_login(world["gyor_manager"])
    response = client.post(
        reverse("activation_decide", args=[approval.pk]), {"decision": "approve"}
    )
    assert response.status_code == 403
    approval.refresh_from_db()
    assert approval.status == ActivationApprovalStatus.PENDING


# --- audit -----------------------------------------------------------------


def test_request_and_decision_are_audited(world):
    from core.audit.models import AuditEvent

    approval = request_activation(
        world["person"], world["project"], actor=world["coordinator"]
    )
    decide_activation(approval, "approve", actor=world["manager"])
    actions = set(
        AuditEvent.objects.filter(action__startswith="activation.").values_list(
            "action", flat=True
        )
    )
    assert {"activation.requested", "activation.approved"} <= actions
