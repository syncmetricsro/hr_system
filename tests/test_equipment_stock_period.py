"""The warehouse report over a reporting period (J7), and the label bug (J10).

The client's complaint was that selecting a year collapsed back into a month
picker, so "the whole of 2026" could not be asked for, and that several months
could not be reported together.

The second thing this file pins is smaller and more embarrassing. The page
rendered the movement *type* by printing the raw enum key, so it showed a
literal lowercase "receipt" and "issue" in every language. That is what the
client reported as untranslated warehouse strings - and the catalog was correct
the whole time, so translating it again would have fixed nothing.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.apps import apps as django_apps
from django.test import override_settings
from django.urls import reverse
from django.utils import translation

if not django_apps.is_installed("features.logistics"):
    pytest.skip("Jober feature set not installed", allow_module_level=True)

from core.reporting.periods import resolve_period  # noqa: E402
from features.logistics.models import EquipmentItem  # noqa: E402
from features.logistics.services import (  # noqa: E402
    equipment_period_report,
    receive_stock,
)

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


@pytest.fixture
def item():
    return EquipmentItem.objects.create(name="Demo boot", size="42")


def _receive(item, when, quantity=1, total_value="10.00"):
    receive_stock(
        received_on=when,
        lines=[
            {"item": item, "quantity": quantity, "total_value": Decimal(total_value)}
        ],
        operation_key=uuid4(),
    )


@pytest.fixture
def spread(item):
    """One receipt in each of January, March and July 2026."""
    _receive(item, date(2026, 1, 15))
    _receive(item, date(2026, 3, 15))
    _receive(item, date(2026, 7, 15))
    return item


def _quantity(report):
    return sum(row["quantity"] or 0 for row in report["by_type"])


# --- the granularities the client asked for ---------------------------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_whole_year_is_one_report(spread):
    """The actual complaint: a year could not be asked for."""
    report = equipment_period_report(resolve_period({"period": "year", "year": "2026"}))
    assert _quantity(report) == 3


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_single_month_still_works(spread):
    report = equipment_period_report(
        resolve_period({"period": "month", "month": "2026-03"})
    )
    assert _quantity(report) == 1


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_several_months_report_as_one_period(spread):
    """January and March together - and July, which was not selected, stays
    out. A span from January to July would have swept it in."""
    period = resolve_period(
        {"period": "months", "month": ["2026-01", "2026-03"]}, today=date(2026, 7, 14)
    )
    report = equipment_period_report(period)
    assert not period.is_contiguous
    assert _quantity(report) == 2


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_an_empty_period_reports_nothing_rather_than_failing(spread):
    report = equipment_period_report(
        resolve_period({"period": "month", "month": "2026-02"})
    )
    assert report["by_type"] == []


# --- J10: the label, not the raw key ----------------------------------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_movement_types_carry_a_translated_label(spread):
    with translation.override("en"):
        report = equipment_period_report(
            resolve_period({"period": "year", "year": "2026"})
        )
        labels = [str(row["label"]) for row in report["by_type"]]
    assert labels == ["Receipt"]
    assert "receipt" not in labels  # the raw key must not reach a template


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_the_hungarian_page_does_not_print_the_raw_enum_key(
    client, django_user_model, spread
):
    """The client reads the system in Hungarian and pointed at this page."""
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)
    # The language comes from the URL prefix (i18n_patterns), not a header -
    # tests otherwise run under the Slovak default.
    with translation.override("hu"):
        url = reverse("equipment_stock")
    response = client.get(url + "?period=year&year=2026")
    body = response.content.decode()
    assert response.status_code == 200
    # "Bevételezés" is the Hungarian for a goods receipt; the raw key is not.
    assert ">receipt<" not in body
    assert "Bevételezés" in body


# --- the page renders the picker back in the state it was given -------------


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_the_page_offers_a_year_option_without_collapsing_to_months(
    client, django_user_model, spread
):
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)
    response = client.get(reverse("equipment_stock") + "?period=year&year=2026")
    assert response.context["period"].kind == "year"
    assert response.context["period"].label == "2026"


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_gapped_month_selection_comes_back_ticked(client, django_user_model, spread):
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)
    response = client.get(
        reverse("equipment_stock") + "?period=months&month=2026-01&month=2026-03"
    )
    ticked = [
        m["value"] for m in response.context["selectable_months"] if m["selected"]
    ]
    assert ticked == ["2026-01", "2026-03"]


@override_settings(EQUIPMENT_STOCK_LEDGER_ENABLED=True)
def test_a_hand_edited_period_falls_back_instead_of_500ing(
    client, django_user_model, spread
):
    manager = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(manager)
    response = client.get(reverse("equipment_stock") + "?period=year&year=banana")
    assert response.status_code == 200
    assert response.context["period"].kind == "month"
