"""Date pickers must not accept a five-digit year.

A native date input always *submits* ISO `YYYY-MM-DD`, so the format was never
the problem — the year was. Unbounded, the spinner happily runs past 9999, and
`12345-06-07` parses as a perfectly valid date, so a mistyped year lands in the
database as a plausible-looking row a few thousand years out and nothing
complains.

`min`/`max` is what caps it. These tests are a sweep rather than a unit test
because the failure mode is *someone adds one more input later* — a per-widget
test would pass while the new field went unbounded.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from django import forms

from core.ui.forms import (
    DATE_MAX,
    DATE_MIN,
    date_input,
    datetime_input,
    month_input,
    month_text_input,
)

REPO = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = [REPO / "templates", REPO / "clients"]
DATED_INPUT = re.compile(
    r'<input[^>]*type="(date|datetime-local|month)"[^>]*>', re.I
)


def _template_files():
    for root in TEMPLATE_DIRS:
        yield from root.rglob("*.html")


def test_every_date_input_in_a_template_is_bounded():
    offenders = []
    for path in _template_files():
        for match in DATED_INPUT.finditer(path.read_text()):
            tag = match.group(0)
            if "min=" not in tag or "max=" not in tag:
                offenders.append(f"{path.relative_to(REPO)}: {tag[:80]}")

    assert offenders == [], "unbounded date inputs:\n" + "\n".join(offenders)


def test_the_helpers_emit_a_four_digit_ceiling():
    for widget in (date_input(), month_input(), month_text_input(), datetime_input()):
        attrs = widget.attrs
        # Exactly four digits, then a separator — never a fifth.
        assert re.match(r"^\d{4}[-T]", attrs["min"]), attrs
        assert re.match(r"^\d{4}[-T]", attrs["max"]), attrs
        assert attrs["min"].startswith("1900") and attrs["max"].startswith("2099")


def test_the_bounds_are_real_dates_not_just_strings():
    import datetime as dt

    assert dt.date.fromisoformat(DATE_MIN) < dt.date.fromisoformat(DATE_MAX)


def test_date_input_is_still_a_date_widget():
    """The point is to add bounds, not to swap the control for a text box.

    Django's ``Input.__init__`` pops ``type`` out of ``attrs`` into
    ``input_type``, so that — not ``attrs`` — is what decides the rendered tag.
    """
    assert isinstance(date_input(), forms.DateInput)
    assert date_input().input_type == "date"
    assert datetime_input().input_type == "datetime-local"
    assert month_input().input_type == "month"


def test_month_text_input_is_a_text_widget_for_charfield_periods():
    """`Payslip.period` is a CharField holding `YYYY-MM`; a DateInput would try
    to localize a value that is already the string we want to render."""
    assert isinstance(month_text_input(), forms.TextInput)
    assert not isinstance(month_text_input(), forms.DateInput)
    assert month_text_input().input_type == "month"
    # Still renders a month picker with the bounds, despite being a TextInput.
    html = month_text_input().render("period", "2026-07")
    assert 'type="month"' in html and 'max="2099-12"' in html
    assert 'value="2026-07"' in html


def test_extra_attributes_survive():
    assert date_input(required=True).attrs["required"] is True
    assert date_input().attrs["max"] == DATE_MAX


@pytest.mark.parametrize(
    "form_path,field",
    [
        ("core.people.forms.PersonForm", "date_of_birth"),
        ("features.payslips.forms.PayslipForm", "issue_date"),
    ],
)
def test_forms_use_the_bounded_widget(form_path, field):
    module_name, class_name = form_path.rsplit(".", 1)
    pytest.importorskip(module_name)
    import importlib

    form_class = getattr(importlib.import_module(module_name), class_name)
    widget = form_class.base_fields[field].widget
    assert widget.attrs.get("max") == DATE_MAX, f"{form_path}.{field} is unbounded"
