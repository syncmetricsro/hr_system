"""SMS templates must exist for the picker to appear (item 16).

`Action.SMS_MANAGE_TEMPLATES` is granted to Manager and implemented nowhere, so
templates were reachable only through Django admin - which needs a superuser no
client role has. And none were seeded, while the SMS panel renders its picker
behind `{% if panel.message_templates %}`: the control never appeared at all,
and the runbook's "pick a template" step had nothing to pick.
"""

from __future__ import annotations

import pytest
from django.apps import apps as django_apps
from django.core.management import call_command

if not django_apps.is_installed("features.messaging"):
    pytest.skip("messaging not installed for this client", allow_module_level=True)

from features.messaging.models import MessageTemplate  # noqa: E402

pytestmark = pytest.mark.django_db


def test_seeding_creates_templates():
    call_command("seed_messaging")
    assert MessageTemplate.objects.filter(is_active=True).count() >= 2


def test_seeding_is_idempotent():
    """Seeds re-run on every staging deploy; duplicates would grow the picker
    a little more each time."""
    call_command("seed_messaging")
    first = MessageTemplate.objects.count()
    call_command("seed_messaging")
    assert MessageTemplate.objects.count() == first


def test_a_reseed_repairs_an_edited_body():
    """update_or_create on `name`, so an admin edit is overwritten rather than
    duplicated. Worth pinning: the alternative silently accumulates near-copies."""
    call_command("seed_messaging")
    template = MessageTemplate.objects.first()
    template.body = "edited by hand"
    template.save(update_fields=["body"])

    call_command("seed_messaging")

    template.refresh_from_db()
    assert template.body != "edited by hand"


def test_the_picker_has_something_to_offer(client, django_user_model):
    """The end-to-end point: the panel hides its picker when the queryset is
    empty, which is why this looked like a missing feature rather than missing
    data."""
    call_command("seed_messaging")
    assert MessageTemplate.objects.filter(is_active=True).exists()
