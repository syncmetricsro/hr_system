"""Re-seeding must not silently undo a rotated demo password.

`demo-jober-2026` is published in this **public** repository, and staging is
internet-reachable, so the staging accounts were rotated away from it on
2026-07-26. `seed_demo` is idempotent and is re-run whenever demo data is
refreshed - if it reset passwords on every run it would quietly republish the
known value, and nothing would report that it had happened.

There is no in-app way to change a password yet (production-readiness item 11,
designed in `docs/product/jober-multi-office-scoping.md` §3b), so a silent
revert here would have to be noticed and fixed from a shell again.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("clients.jober.demo"):
    pytest.skip(
        "Jober demo seeds are not installed for this client", allow_module_level=True
    )

from django.core.management import call_command  # noqa: E402

from clients.jober.demo.management.commands.seed_demo import (  # noqa: E402
    DEMO_PASSWORD,
    DEMO_USERS,
)
from core.accounts.models import User  # noqa: E402

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]

ROTATED = "a-rotated-staging-password-2026"


def _manager() -> User:
    return User.objects.get(email="manazer@demo.jober.test")


def test_first_seed_sets_the_builtin_password():
    call_command("seed_demo")
    assert User.objects.filter(email__endswith="@demo.jober.test").count() == len(
        DEMO_USERS
    )
    assert _manager().check_password(DEMO_PASSWORD)


def test_reseeding_keeps_a_rotated_password():
    call_command("seed_demo")
    user = _manager()
    user.set_password(ROTATED)
    user.save(update_fields=["password"])

    call_command("seed_demo")

    user.refresh_from_db()
    assert user.check_password(ROTATED), (
        "re-seeding republished the known demo password"
    )
    assert not user.check_password(DEMO_PASSWORD)


def test_reseeding_still_repairs_everything_else():
    """Preserving the password must not turn the seed into a no-op: role,
    names and is_active are still corrected on an existing account."""
    call_command("seed_demo")
    user = _manager()
    user.set_password(ROTATED)
    user.first_name = "Wrong"
    user.is_active = False
    user.save(update_fields=["password", "first_name", "is_active"])

    call_command("seed_demo")

    user.refresh_from_db()
    assert user.first_name == "Manažér"
    assert user.is_active is True
    assert user.check_password(ROTATED)


def test_reset_passwords_flag_forces_the_builtin_password_back():
    call_command("seed_demo")
    user = _manager()
    user.set_password(ROTATED)
    user.save(update_fields=["password"])

    call_command("seed_demo", "--reset-passwords")

    user.refresh_from_db()
    assert user.check_password(DEMO_PASSWORD)
