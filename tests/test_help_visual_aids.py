"""The Getting Started visual aids must stay true, translated and client-neutral.

These diagrams shipped on 2026-07-27 describing a system that did not exist: a
"Field" navigation tab that is not in the nav, example offices in Bratislava
and Košice (Jober operates from Velký Meder, Győr and Dunajská Streda), a
hardcoded `JOBER` wordmark in a template CorvinumEU also renders, and 39 of 59
strings with no translation — so a Slovak reader saw English.

A picture asserts things prose does not have to. "Which tabs exist" is
checkable, and these tests check it, because the failure mode is a confident
diagram of the wrong product rather than a crash.
"""

from __future__ import annotations

import re

import pytest
from django.template.loader import render_to_string
from django.utils import translation

pytestmark = pytest.mark.jober_only

# The tabs the shell actually renders (templates/layouts/base.html).
REAL_TABS = {"People", "Projects", "Compliance", "Accommodation", "Reports", "Help"}


def _render(**context) -> str:
    context.setdefault("BRAND_NAME", "Jober")
    context.setdefault("OFFICES_IN_USE", True)
    return render_to_string("help/getting-started.html", context)


def test_mock_navbar_only_shows_tabs_that_exist():
    """The diagram invented a "Field" tab. A reader cannot tell a mocked-up
    tab from a real one, so anything drawn here has to exist in the shell."""
    with translation.override("en"):
        html = _render()
    tabs = set(
        re.findall(
            r'<span class="help-mock-tab[^"]*">(?:<span[^>]*>\d</span>)?([^<]+)</span>',
            html,
        )
    )
    invented = {t.strip() for t in tabs} - REAL_TABS - {"Your office", "Your role"}
    assert not invented, f"diagram shows tabs the app does not have: {invented}"


def test_no_offices_the_client_does_not_operate():
    """Bratislava and Košice were used as example offices for a client whose
    offices are Velký Meder, Győr and Dunajská Streda."""
    with translation.override("en"):
        html = _render()
    for city in ("Bratislava", "Košice", "Kosice"):
        assert city not in html, f"help diagram names {city}, which is not an office"


def test_template_is_client_neutral():
    """Shared template: CorvinumEU renders the same file, so the wordmark comes
    from BRAND_NAME rather than being written in."""
    html = _render(BRAND_NAME="CorvinumEU")
    assert "CorvinumEU" in html
    assert "JOBER" not in html


def test_office_diagram_is_hidden_on_a_single_site_install():
    """The boundary diagram explains something a single-site client does not
    have. The surrounding prose covers that case in words; a picture cannot."""
    assert "help-office-flow" not in _render(OFFICES_IN_USE=False)
    assert "help-office-flow" in _render(OFFICES_IN_USE=True)


@pytest.mark.parametrize("language", ["sk", "hu", "uk"])
def test_visual_aid_strings_are_translated(language):
    """The strings were wrapped in {% trans %} but never translated, which
    renders English inside a Slovak page. Wrapping only makes a string
    extractable; it is the catalog that makes it translated."""
    probes = [
        "Module Tabs",
        "Office Scope",
        "User Role",
        "Manager / Admin",
        "Full Operational Access",
        "Read-Only Oversight",
        "Available candidate",
        "Add Worker",
        "Your office",
    ]
    with translation.override(language):
        html = _render()
    untranslated = [p for p in probes if p in html]
    assert not untranslated, f"{language}: still rendering English: {untranslated}"
