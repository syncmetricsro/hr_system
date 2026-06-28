from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.feedback.models import FeedbackLink, FeedbackSubmission

pytestmark = pytest.mark.django_db


@pytest.fixture
def link():
    return FeedbackLink.objects.create(label="DHL gate", token="abc123")


@pytest.fixture
def make_user(django_user_model):
    def _make(role):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )
    return _make


def test_public_form_no_login_and_submits(client, link):
    url = reverse("feedback_form", args=[link.token])
    assert client.get(url).status_code == 200  # public, no login
    resp = client.post(url, {"message": "Great team", "rating": "5"})
    assert resp.status_code == 200
    sub = FeedbackSubmission.objects.get()
    assert sub.message == "Great team" and sub.rating == 5


def test_public_form_requires_message(client, link):
    client.post(reverse("feedback_form", args=[link.token]), {"message": ""})
    assert not FeedbackSubmission.objects.exists()


def test_inactive_or_unknown_token_404(client, link):
    link.is_active = False
    link.save()
    assert client.get(reverse("feedback_form", args=[link.token])).status_code == 404
    assert client.get(reverse("feedback_form", args=["nope"])).status_code == 404


def test_inbox_manager_only(client, link, make_user):
    FeedbackSubmission.objects.create(link=link, message="hi")
    # recruiter denied
    client.force_login(make_user("recruiter"))
    assert client.get(reverse("feedback_inbox")).status_code == 403
    # manager allowed
    client.logout()
    client.force_login(make_user("manager"))
    body = client.get(reverse("feedback_inbox")).content.decode("utf-8")
    assert "hi" in body


def test_purge_feedback_command(link):
    from django.core.management import call_command

    old = FeedbackSubmission.objects.create(link=link, message="old")
    FeedbackSubmission.objects.filter(pk=old.pk).update(created_at=timezone.now() - dt.timedelta(days=60))
    FeedbackSubmission.objects.create(link=link, message="recent")
    call_command("purge_feedback")
    remaining = list(FeedbackSubmission.objects.values_list("message", flat=True))
    assert remaining == ["recent"]
