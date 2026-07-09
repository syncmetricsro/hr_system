from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from core.accounts.models import Role, User
from core.audit.models import AuditEvent

pytestmark = pytest.mark.django_db

EMAIL = "admin@jober.example"
PASSWORD = "a-strong-deploy-password"


@pytest.fixture
def superuser_env(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", EMAIL)
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", PASSWORD)


def test_creates_manager_superuser(superuser_env):
    call_command("ensure_superuser")
    user = User.objects.get(email=EMAIL)
    assert user.is_superuser and user.is_staff and user.is_active
    assert user.role == Role.MANAGER
    assert user.check_password(PASSWORD)
    assert AuditEvent.objects.filter(action="accounts.superuser_created").exists()


def test_is_idempotent(superuser_env):
    call_command("ensure_superuser")
    call_command("ensure_superuser")  # must not raise
    assert User.objects.filter(email=EMAIL).count() == 1


def test_repairs_demoted_account(superuser_env):
    User.objects.create_user(email=EMAIL, password=PASSWORD, role=Role.OBSERVER, is_staff=False)
    call_command("ensure_superuser")
    user = User.objects.get(email=EMAIL)
    assert user.is_superuser and user.is_staff
    assert user.role == Role.MANAGER
    assert AuditEvent.objects.filter(action="accounts.superuser_ensured").exists()


def test_errors_when_env_unset(monkeypatch):
    monkeypatch.delenv("DJANGO_SUPERUSER_EMAIL", raising=False)
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
    with pytest.raises(CommandError):
        call_command("ensure_superuser")


def test_skip_if_unset_does_not_raise(monkeypatch):
    monkeypatch.delenv("DJANGO_SUPERUSER_EMAIL", raising=False)
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
    call_command("ensure_superuser", "--skip-if-unset")
    assert not User.objects.exists()
