"""Shared form-widget helpers.

Currently just dates. A native ``<input type="date">`` renders in the browser's
locale but always *submits* ISO ``YYYY-MM-DD``, so the format was never the
problem — the year was. Without bounds the spinner happily accepts five- and
six-digit years, and `12345-06-07` is a valid date to the parser, so a typo
sails through validation and lands in the database as a plausible-looking row a
few thousand years out.

``min``/``max`` are what actually cap the year; browsers refuse out-of-range
values in the picker and mark the field invalid on submit. Server-side
validation is unchanged and still authoritative — this stops the typo at the
keyboard, it does not replace anything.
"""

from __future__ import annotations

from django import forms

#: Wide enough for a date of birth at one end and a contract end date at the
#: other, narrow enough that a four-digit year is the only thing that fits.
DATE_MIN = "1900-01-01"
DATE_MAX = "2099-12-31"
MONTH_MIN = "1900-01"
MONTH_MAX = "2099-12"


def date_attrs(**extra) -> dict:
    """Attributes for a bounded date input, for raw widgets and templates."""
    return {"type": "date", "min": DATE_MIN, "max": DATE_MAX, **extra}


def date_input(**extra) -> forms.DateInput:
    return forms.DateInput(attrs=date_attrs(**extra))


def datetime_input(**extra) -> forms.DateTimeInput:
    """``datetime-local`` takes the same bounds with a time component."""
    return forms.DateTimeInput(
        attrs={
            "type": "datetime-local",
            "min": f"{DATE_MIN}T00:00",
            "max": f"{DATE_MAX}T23:59",
            **extra,
        }
    )


def month_attrs(**extra) -> dict:
    return {"type": "month", "min": MONTH_MIN, "max": MONTH_MAX, **extra}


def month_input(**extra) -> forms.DateInput:
    """A ``YYYY-MM`` picker for a **DateField**.

    Pair with ``input_formats=["%Y-%m"]`` on the field.
    """
    return forms.DateInput(format="%Y-%m", attrs=month_attrs(**extra))


def month_text_input(**extra) -> forms.TextInput:
    """The same picker for a **CharField** that stores ``YYYY-MM`` verbatim.

    A ``DateInput`` would try to localize a value that is already a string;
    ``TextInput`` renders it untouched while the browser still shows a month
    picker and enforces the bounds.
    """
    return forms.TextInput(attrs=month_attrs(**extra))
