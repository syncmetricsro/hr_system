from __future__ import annotations

import pytest
from django.utils import translation
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from core.audit.models import AuditEvent
from core.people.models import LifecycleStatus, Person
from core.projects.models import Project
from core.projects.services import WorkflowError, activate_on_project
from features.checklists.models import (
    ChecklistItemTemplate,
    ChecklistTemplate,
    PersonChecklistItem,
)
from features.checklists.services import (
    activation_gate,
    ensure_person_checklist,
    missing_critical_labels,
    set_item_state,
)
from features.checklists.views import toggle_item_view

pytestmark = pytest.mark.django_db

FLAGS_ON = {"checklists": True}


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="cl-manager@demo.jober.test", password="x", role="manager"
    )


@pytest.fixture
def person():
    return Person.objects.create(first_name="Test", last_name="Candidate")


@pytest.fixture
def template():
    tpl = ChecklistTemplate.objects.create(name="Global activation")
    ChecklistItemTemplate.objects.create(template=tpl, label="Identity document verified", critical=True, order=1)
    ChecklistItemTemplate.objects.create(template=tpl, label="Welcome call made", critical=False, order=2)
    return tpl


def _post_toggle(user, item):
    # The toggle URL is only mounted for clients with the flag on (e.g.
    # corvinum_eu), so tests under Jober settings call the view directly.
    request = RequestFactory().post(f"/checklist/{item.pk}/toggle/")
    request.user = user
    return toggle_item_view(request, item_pk=item.pk)


def test_ensure_checklist_is_idempotent(person, template):
    first = ensure_person_checklist(person)
    second = ensure_person_checklist(person)
    assert len(first) == len(second) == 2
    assert PersonChecklistItem.objects.filter(person=person).count() == 2


def test_missing_critical_only_counts_critical(person, template):
    with translation.override("en"):  # labels localize via the db_trans pattern
        assert missing_critical_labels(person) == ["Identity document verified"]
    item = PersonChecklistItem.objects.get(person=person, item_template__critical=True)
    set_item_state(item, done=True)
    assert missing_critical_labels(person) == []


def test_set_item_state_records_identity_and_audits(person, template, manager):
    item = ensure_person_checklist(person)[0]
    set_item_state(item, done=True, actor=manager)
    item.refresh_from_db()
    assert item.done and item.done_by == manager and item.done_at is not None
    assert AuditEvent.objects.filter(action="checklist.item_ticked").exists()


def test_gate_noops_when_flag_off(settings, person, template):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "checklists": False}
    activation_gate(person)  # open critical item, but flag off -> no error


def test_activation_blocked_then_allowed(settings, person, template, manager):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}
    project = Project.objects.create(name="CL-Proj", code="CLPRJ")
    # Instantiate outside the activation transaction (in real flow the person
    # page's panel does this); the blocked activation must not roll them away.
    ensure_person_checklist(person)

    with translation.override("en"), pytest.raises(WorkflowError, match="Identity document verified"):
        activate_on_project(person, project, actor=manager)

    item = PersonChecklistItem.objects.get(person=person, item_template__critical=True)
    set_item_state(item, done=True, actor=manager)
    activate_on_project(person, project, actor=manager)
    person.refresh_from_db()
    assert person.lifecycle_status == LifecycleStatus.WORKING


def test_toggle_view_flips_item(settings, person, template, manager):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}
    item = ensure_person_checklist(person)[0]
    resp = _post_toggle(manager, item)
    assert resp.status_code == 302
    item.refresh_from_db()
    assert item.done


def test_toggle_view_denied_for_observer(settings, person, template, django_user_model):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, **FLAGS_ON}
    observer = django_user_model.objects.create_user(
        email="cl-observer@demo.jober.test", password="x", role="observer"
    )
    item = ensure_person_checklist(person)[0]
    with pytest.raises(PermissionDenied):
        _post_toggle(observer, item)
    item.refresh_from_db()
    assert not item.done
