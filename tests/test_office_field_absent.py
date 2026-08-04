"""An install with no offices should not ask which office.

CorvinumEU populates no ``Office`` rows on purpose — office separation is a
Jober concept (ADR 0026). Until 2026-08-04 the picker still rendered, as an
empty dropdown, on every form that offers one: a required-looking question with
no possible answer.

The condition is **the data, not the client**. Nothing here checks who is
running; seed one office and every field returns. That is what keeps `core`
free of client branching, and it is why the second half of this file matters as
much as the first: Jober's scoping must be provably untouched.
"""

from __future__ import annotations

import pytest

from core.accounts.models import Role
from core.offices.models import Office
from core.people.forms import PersonForm
from core.projects.forms import ProjectForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        email="office-form-mgr@demo.test", password="x", role=Role.MANAGER
    )


# --- no offices: the question disappears -----------------------------------


@pytest.mark.parametrize("form_class", [ProjectForm, PersonForm])
def test_the_office_field_is_removed_when_no_offices_exist(form_class, manager):
    assert not Office.objects.exists()

    form = form_class(user=manager)

    assert "office" not in form.fields
    assert "office" not in form.as_p()


def test_a_project_can_be_created_without_choosing_an_office(manager):
    form = ProjectForm(
        data={"name": "Partner Kft", "code": "PKFT", "is_active": "on"},
        user=manager,
    )

    assert form.is_valid(), form.errors
    project = form.save()
    assert project.office_id is None


def test_the_coordinator_help_text_stops_promising_office_narrowing(manager):
    """It read 'Only coordinators of the selected office can be chosen.' — a
    boundary this install does not have, next to a picker that is not there."""
    form = ProjectForm(user=manager)

    help_text = str(form.fields["responsible_coordinators"].help_text)
    assert "office" not in help_text.lower()


def test_every_coordinator_is_offerable_when_there_are_no_offices(
    manager, django_user_model
):
    """With no offices there is nothing to narrow by, so narrowing to none
    would leave the field permanently empty."""
    coordinator = django_user_model.objects.create_user(
        email="office-form-coord@demo.test", password="x", role=Role.COORDINATOR
    )

    form = ProjectForm(user=manager)

    assert coordinator in form.fields["responsible_coordinators"].queryset


# --- offices exist: Jober's behaviour is unchanged -------------------------


def test_the_field_returns_as_soon_as_an_office_exists(manager):
    """The switch is data-driven, so this is the whole proof that nothing was
    special-cased per client."""
    Office.objects.create(name="Velký Meder", code="VM", country="SK")

    assert "office" in ProjectForm(user=manager).fields


def test_a_manager_still_only_sees_their_own_offices(manager):
    vm = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    Office.objects.create(name="Győr", code="GYR", country="HU")
    manager.offices.set([vm])

    field = ProjectForm(user=manager).fields["office"]

    assert list(field.queryset) == [vm]
    # A single office is pre-selected, as before.
    assert field.initial == vm
