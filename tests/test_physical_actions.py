"""Buttons that reach outside the application must say so (ADR 0034).

Most controls in this product move numbers between screens. A few cause
something to happen in the physical world - money is paid, a real message
leaves the building, gear or keys change hands, a person travels. The owner
asked for those to be unmistakable, and the marker is three things together:
the ``button-physical`` class, the fixed *Real-world action* tooltip heading,
and a visible consequence caption.

Any one of the three alone degrades quietly - a class with no words, or words
nobody notices next to a button that looks like every other button. So the
tests here defend the trio rather than the styling, and they name the specific
buttons, because the failure this guards against is a future edit that quietly
demotes *Mark cycle settled* back to an ordinary grey button.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext


REPO = Path(__file__).resolve().parent.parent
BUTTON_TAG = re.compile(r"<button\b[^>]*>", re.S)
TOOLTIP_HEADING = re.compile(r'data-tooltip-heading="\{%\s*trans\s*(["\'])(.+?)\1')

# The one phrase, everywhere. Repetition is the point: it is what makes the
# heading recognizable rather than just another sentence.
HEADING = "Real-world action"

# (template, label fragment) - each of these must carry the marker. Ordinary
# buttons are free to change; these are a promise to the office.
MARKED_BUTTONS = [
    ("templates/partials/ledger_cycle.html", "Mark cycle settled"),
    ("templates/pages/payslips.html", "Send encrypted PDF"),
    ("templates/panels/messaging_sms.html", "Send SMS"),
    ("templates/panels/messaging_offer_email.html", "Send offer"),
    ("templates/panels/logistics_equipment.html", "Issue equipment"),
    ("templates/panels/logistics_equipment.html", "Flag unreturned"),
    ("templates/panels/logistics_equipment.html", "Return"),
    ("templates/pages/equipment_reviews.html", "Approve charge"),
    ("templates/panels/logistics_room.html", "Assign room"),
    ("templates/panels/logistics_room.html", "Release room"),
    ("templates/pages/person_detail.html", "Exit to Available"),
    ("templates/pages/person_detail.html", "Exit to Inactive"),
    ("templates/pages/person_detail.html", "Schedule trial"),
    ("templates/pages/person_detail.html", "Skip the trial and start readiness"),
    ("templates/pages/person_detail.html", "Record medical date"),
    ("templates/pages/certificate_form.html", "Save certificate"),
]


def _templates():
    roots = [REPO / "templates", *(REPO / "clients").glob("*/templates")]
    for root in roots:
        yield from sorted(root.rglob("*.html"))


def _physical_buttons(text):
    return [
        tag.group(0)
        for tag in BUTTON_TAG.finditer(text)
        if "button-physical" in tag.group(0)
    ]


@pytest.mark.parametrize("template,label", MARKED_BUTTONS)
def test_the_named_buttons_carry_the_marker(template, label):
    text = (REPO / template).read_text(encoding="utf-8")
    tags = [
        match
        for match in BUTTON_TAG.finditer(text)
        if label in text[match.end() : match.end() + 220]
    ]
    assert tags, f"{label} is no longer a button in {template}"
    assert any("button-physical" in tag.group(0) for tag in tags), (
        f"{label} in {template} lost its real-world marker"
    )


def test_every_physical_button_explains_itself():
    """Class, heading, and specific tooltip travel together or not at all."""
    incomplete = []
    for path in _templates():
        for tag in _physical_buttons(path.read_text(encoding="utf-8")):
            if "data-tooltip-heading" not in tag or "data-tooltip=" not in tag:
                incomplete.append(f"{path.relative_to(REPO)}: {tag[:90]}")
    assert not incomplete, "physical buttons without a tooltip heading:\n" + "\n".join(
        incomplete
    )


def test_every_marked_screen_carries_a_visible_caption():
    """The caption is the part that works without a mouse and without hover."""
    missing = []
    for path in _templates():
        text = path.read_text(encoding="utf-8")
        if _physical_buttons(text) and "action-consequence" not in text:
            missing.append(str(path.relative_to(REPO)))
    assert not missing, (
        "physical buttons with no visible consequence line:\n" + "\n".join(missing)
    )


def test_the_heading_never_drifts():
    """One phrase across the product; a second one would dilute the first.

    Ordinary tooltips use headings freely - form fields name themselves that
    way. Only the physical buttons are held to the single phrase.
    """
    found = set()
    for path in _templates():
        for tag in _physical_buttons(path.read_text(encoding="utf-8")):
            found.update(match.group(2) for match in TOOLTIP_HEADING.finditer(tag))
    assert HEADING in found
    assert found == {HEADING}, f"competing real-world headings: {sorted(found)}"


def test_the_confirmation_dialog_can_show_the_real_world_band():
    dialog = (REPO / "templates/partials/confirm_dialog.html").read_text(
        encoding="utf-8"
    )
    source = (REPO / "static/src/js/app.js").read_text(encoding="utf-8")

    assert 'id="confirm-dialog-physical"' in dialog
    assert "hidden" in dialog
    # The dialog's own description list must include it, or a screen reader
    # never hears the strongest sentence on the screen.
    assert "aria-describedby" in dialog and "confirm-dialog-physical" in dialog

    assert 'classList.contains("button-physical")' in source
    assert 'getElementById("confirm-dialog-physical")' in source
    # Reset on close: an ordinary confirmation must not inherit the band from
    # whatever was confirmed before it.
    assert "setPhysical(false)" in source


def test_the_stripe_is_a_shape_not_only_a_colour():
    """Colour alone fails greyscale and colour-vision deficiency.

    The same reasoning the chart tokens in this stylesheet are built on. If the
    striped edge is ever dropped for a plain fill, the marker stops working for
    the people most likely to miss a warning.
    """
    css = (REPO / "static/src/css/app.css").read_text(encoding="utf-8")

    assert ".button-physical {" in css
    assert ".button-physical::before {" in css
    assert "repeating-linear-gradient" in css.split(".button-physical::before {")[1]
    assert ".action-consequence {" in css
    assert ".confirm-physical {" in css


@pytest.mark.django_db
def test_a_manager_actually_sees_the_marker_on_a_person_page(client, django_user_model):
    """A template can pass every scan above and still be gated off in the app."""
    from core.people.models import Person

    manager = django_user_model.objects.create_user(
        email="physical-mgr@demo.jober.test", password="x", role="manager"
    )
    person = Person.objects.create(first_name="Fictional", last_name="Worker")
    client.force_login(manager)

    response = client.get(reverse("person_detail", args=[person.pk]))
    body = response.content.decode()

    assert "button-physical" in body
    assert "action-consequence" in body
    with translation.override(response.headers["Content-Language"]):
        assert gettext(HEADING) in body
