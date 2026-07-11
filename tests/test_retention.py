from __future__ import annotations

import pytest
from django.apps import apps as django_apps

if not django_apps.is_installed("features.feedback"):
    pytest.skip("features.feedback is not installed for this client", allow_module_level=True)


import datetime as dt

import pytest
from django.core.management import call_command
from django.utils import timezone

from core.retention.services import registered, run_all
from features.blacklist.services import propose_case
from features.feedback.models import FeedbackLink, FeedbackSubmission
from core.people.models import Person

pytestmark = pytest.mark.django_db


def test_feature_purges_are_registered():
    names = registered()
    assert "feedback" in names
    assert "blacklist_fingerprints" in names


def test_run_all_purges_expired_rows(django_user_model):
    # Expired feedback submission…
    link = FeedbackLink.objects.create(label="QR")
    sub = FeedbackSubmission.objects.create(link=link, message="old")
    FeedbackSubmission.objects.filter(pk=sub.pk).update(
        created_at=timezone.now() - dt.timedelta(days=90)
    )
    # …and an expired blacklist fingerprint.
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    person = Person.objects.create(first_name="A", last_name="B")
    case = propose_case(person, identifier="GONE-1", actor=manager)
    case.fingerprints.update(expires_at=dt.date(2000, 1, 1))

    results = run_all()
    assert results["feedback"] == 1
    assert results["blacklist_fingerprints"] == 1
    assert not FeedbackSubmission.objects.filter(pk=sub.pk).exists()
    assert not case.fingerprints.exists()


def test_run_retention_command_runs(capsys):
    call_command("run_retention")  # no expired rows: still succeeds
