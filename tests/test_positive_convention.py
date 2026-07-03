from __future__ import annotations

from decimal import Decimal

import pytest

from apps.finance.models import (
    FinanceCategory,
    FinanceCategoryKind,
    FinancialMonth,
)
from apps.finance.services import (
    FinanceError,
    record_financial_month,
    recompute_month,
    set_line_item,
)
from apps.logistics.models import Accommodation, Room
from apps.logistics.services import set_assignment_rate, set_room_rate, assign_room
from apps.people.models import Person
from apps.projects.models import Project

pytestmark = pytest.mark.django_db


@pytest.fixture
def month(django_user_model):
    actor = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    project = Project.objects.create(name="DHL", code="DHLBA")
    return actor, FinancialMonth.objects.create(project=project, year=2026, month=5), project


def test_positive_net_is_revenue_minus_cost(month):
    actor, m, _p = month
    wage = FinanceCategory.objects.create(label="Gross wage", kind=FinanceCategoryKind.COST)
    invoice = FinanceCategory.objects.create(label="Client invoices", kind=FinanceCategoryKind.REVENUE)
    set_line_item(m, wage, "12000", actor=actor)     # positive cost
    set_line_item(m, invoice, "18000", actor=actor)  # positive revenue
    recompute_month(m, actor=actor)
    m.refresh_from_db()
    assert m.cost == Decimal("12000")     # stored positive, not -12000
    assert m.revenue == Decimal("18000")
    assert m.net == Decimal("6000")       # revenue - cost


def test_line_item_rejects_negative(month):
    actor, m, _p = month
    cat = FinanceCategory.objects.create(label="Fuel", kind=FinanceCategoryKind.COST)
    with pytest.raises(FinanceError):
        set_line_item(m, cat, "-100", actor=actor)


def test_record_month_rejects_negative(month):
    actor, _m, project = month
    with pytest.raises(FinanceError):
        record_financial_month(project, 2026, 6, "18000", "-5000", actor=actor)


def test_room_rate_rejects_negative(django_user_model):
    actor = django_user_model.objects.create_user(email="r@demo.jober.test", password="x", role="manager")
    room = Room.objects.create(accommodation=Accommodation.objects.create(name="U"), label="1")
    with pytest.raises(ValueError):
        set_room_rate(room, "-50", actor=actor)


def test_assignment_rate_rejects_negative(django_user_model):
    actor = django_user_model.objects.create_user(email="c@demo.jober.test", password="x", role="coordinator")
    room = Room.objects.create(accommodation=Accommodation.objects.create(name="U"), label="1", capacity=1)
    person = Person.objects.create(first_name="A", last_name="B")
    assignment = assign_room(person, room, actor=actor)
    with pytest.raises(ValueError):
        set_assignment_rate(assignment, "-10", actor=actor)
