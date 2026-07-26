"""Every office must have its own staff, and each project its own office's
coordinator.

The demo's headline is office separation, and until 2026-07-26 it could only be
shown in one direction: all three working accounts belonged to Velký Meder, so
"the VM manager cannot see Győr" was demonstrable but "the Győr manager cannot
see VM" was not. One direction looks like a filter; both look like a boundary.

The seed also assigned *every* project to the Velký Meder coordinator,
including the four in other offices — leaving them formally responsible for
work they get a 403 on. That is the kind of incoherence a client notices by
asking an obvious question ("so who runs the Győr contracts?"), not by reading
code.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.core.management import call_command
from django.urls import reverse

if not django_apps.is_installed("clients.jober.demo"):
    pytest.skip("Jober demo seeds are not installed", allow_module_level=True)

from clients.jober.demo.management.commands.seed_demo import (  # noqa: E402
    DEMO_DOMAIN,
    DEMO_USERS,
)
from core.accounts.models import Role, User  # noqa: E402
from core.offices.models import Office  # noqa: E402
from core.projects.models import Project  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

OFFICE_CODES = ("VM", "GYR", "DS")


@pytest.fixture
def seeded():
    call_command("seed_demo")
    call_command("seed_people")


def test_every_office_has_a_manager_recruiter_and_coordinator(seeded):
    for code in OFFICE_CODES:
        office = Office.objects.get(code=code)
        roles = set(User.objects.filter(offices=office).values_list("role", flat=True))
        assert {Role.MANAGER, Role.RECRUITER, Role.COORDINATOR} <= roles, (
            f"office {code} is missing staff roles: {roles}"
        )


def test_each_staff_account_belongs_to_exactly_one_office(seeded):
    """Membership in several offices would quietly defeat the demo: the
    account's pages would look identical to the Observer's."""
    for local_part, _role, _first, _last, office_code in DEMO_USERS:
        user = User.objects.get(email=f"{local_part}@{DEMO_DOMAIN}")
        if office_code is None:
            assert user.offices.count() == 0
        else:
            assert [o.code for o in user.offices.all()] == [office_code]


def test_observer_holds_no_office_membership(seeded):
    """Cross-office visibility must stay a role bypass. Granting the Observer
    all three offices would produce the same screens by a different mechanism,
    and would silently survive a change to user_office_scope."""
    observer = User.objects.get(email=f"pozorovatel@{DEMO_DOMAIN}")
    assert observer.role == Role.OBSERVER
    assert observer.offices.count() == 0


def test_each_project_is_run_by_a_coordinator_of_its_own_office(seeded):
    for project in Project.objects.select_related("office"):
        coordinators = list(project.responsible_coordinators.all())
        assert coordinators, f"{project.code} has no responsible coordinator"
        for coordinator in coordinators:
            assert project.office in coordinator.offices.all(), (
                f"{project.code} ({project.office.code}) is run by "
                f"{coordinator.email}, who cannot open it"
            )


def test_the_boundary_is_reciprocal(client, seeded):
    """The point of the whole change: each office's manager sees their own
    projects and is refused the others', in *both* directions."""
    gyor_project = Project.objects.get(code="WEB")
    vm_project = Project.objects.get(code="DHLBA")

    client.force_login(User.objects.get(email=f"manazer@{DEMO_DOMAIN}"))
    assert (
        client.get(reverse("project_detail", args=[vm_project.pk])).status_code == 200
    )
    assert (
        client.get(reverse("project_detail", args=[gyor_project.pk])).status_code == 403
    )

    client.force_login(User.objects.get(email=f"manazer.gyor@{DEMO_DOMAIN}"))
    assert (
        client.get(reverse("project_detail", args=[gyor_project.pk])).status_code == 200
    )
    assert (
        client.get(reverse("project_detail", args=[vm_project.pk])).status_code == 403
    )


def test_reseeding_does_not_multiply_office_membership(seeded):
    """`offices.set()` replaces rather than appends; `add()` would accumulate
    across runs until every account spanned every office and the demo silently
    stopped demonstrating anything."""
    call_command("seed_people")
    manager = User.objects.get(email=f"manazer.gyor@{DEMO_DOMAIN}")
    assert manager.offices.count() == 1
    assert Project.objects.get(code="WEB").responsible_coordinators.count() == 1
