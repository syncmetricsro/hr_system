from __future__ import annotations

import datetime as dt

import pytest

from core.accounts.permissions import Action, can
from features.logistics.models import TransportWeek
from features.logistics.services import record_transport_week
from core.projects.models import Project

pytestmark = pytest.mark.django_db

WEEK = dt.date(2026, 6, 22)


@pytest.fixture
def setup(django_user_model):
    coord = django_user_model.objects.create_user(
        email="c@demo.jober.test", password="x", role="coordinator"
    )
    project = Project.objects.create(name="DHL", code="DHLBA")
    return coord, project


def test_record_transport_week_creates(setup):
    coord, project = setup
    week = record_transport_week(project, WEEK, 12, actor=coord)
    assert week.headcount == 12
    assert TransportWeek.objects.count() == 1


def test_record_is_idempotent_per_week(setup):
    coord, project = setup
    record_transport_week(project, WEEK, 12, actor=coord)
    record_transport_week(project, WEEK, 15, actor=coord)
    assert TransportWeek.objects.count() == 1
    assert TransportWeek.objects.get().headcount == 15


def test_transport_rbac(django_user_model):
    coord = django_user_model.objects.create_user(email="c2@demo.jober.test", password="x", role="coordinator")
    observer = django_user_model.objects.create_user(email="o@demo.jober.test", password="x", role="observer")
    assert can(coord, Action.TRANSPORT_RECORD)
    assert not can(observer, Action.TRANSPORT_RECORD)
