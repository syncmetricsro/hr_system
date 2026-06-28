from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse

from apps.logistics.services import record_transport_week
from apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_transport_trends_requires_login(client):
    resp = client.get(reverse("transport_trends"))
    assert resp.status_code == 302
    assert reverse("login") in resp.headers["Location"]


def test_transport_trends_shows_company_total(client, django_user_model):
    p1 = Project.objects.create(name="Alpha", code="ALPHA")
    p2 = Project.objects.create(name="Beta", code="BETA")
    week = dt.date(2026, 6, 22)
    record_transport_week(p1, week, 10)
    record_transport_week(p2, week, 5)
    user = django_user_model.objects.create_user(email="m@demo.jober.test", password="x", role="manager")
    client.force_login(user)
    body = client.get(reverse("transport_trends")).content.decode("utf-8")
    assert "Alpha" in body and "Beta" in body
    assert "15" in body  # company total for the week (10 + 5)
