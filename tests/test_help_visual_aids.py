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
from pathlib import Path

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


# --- the screenshot/illustration pipeline (J9) -------------------------------
#
# The section above guards a hand-built HTML mock of the UI. The plan's core
# argument is that such a mock drifts from the product while a screenshot
# cannot, so the mock is on its way out - but only once real captures exist to
# replace it. These tests guard the pipeline that will carry them, and they are
# deliberately written to pass with zero images so the scaffolding can land
# before the assets do.

REPO = Path(__file__).resolve().parent.parent
HELP_TEMPLATES = sorted((REPO / "templates" / "help").glob("*.html"))

STATIC_REF = re.compile(r"""\{%\s*static\s+["']([^"']+)["']\s*%\}""")
IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
ALT_ATTR = re.compile(r"""\balt\s*=\s*["']([^"']*)["']""", re.IGNORECASE)


def _static_refs() -> list[tuple[str, str]]:
    refs = []
    for path in HELP_TEMPLATES:
        for ref in STATIC_REF.findall(path.read_text(encoding="utf-8")):
            refs.append((path.name, ref))
    return refs


def test_the_help_static_directory_is_copied_into_the_image():
    """Static subdirectories are copied individually in the Dockerfile, so a
    missing line means the files exist in git and 404 in production. That has
    already happened once, to the avatars."""
    dockerfile = (REPO / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY static/help /app/static/help" in dockerfile


def test_every_referenced_asset_is_discoverable_by_staticfiles():
    """`{% static %}` builds a URL without checking anything exists. This is
    the check that catches a file placed where STATICFILES_DIRS never looks."""
    from django.contrib.staticfiles.finders import find

    missing = [f"{name} -> {ref}" for name, ref in _static_refs() if find(ref) is None]
    assert not missing, f"referenced but not servable: {missing}"


@pytest.mark.parametrize("path", HELP_TEMPLATES, ids=lambda p: p.name)
def test_every_help_image_has_translatable_alt_text(path):
    """Alt text is content in a four-language Help area, not decoration -
    and hardcoding it ships English to a Slovak reader."""
    source = path.read_text(encoding="utf-8")
    for tag in IMG_TAG.findall(source):
        alt = ALT_ATTR.search(tag)
        assert alt is not None, f"{path.name}: <img> without alt: {tag[:80]}"
        value = alt.group(1).strip()
        assert value, f"{path.name}: <img> with empty alt: {tag[:80]}"
        assert "{%" in value or "{{" in value, (
            f"{path.name}: alt text is not translatable: {value!r}"
        )


def test_illustrations_are_shared_across_languages():
    """Illustrations are textless by construction, so a per-language variant
    means someone baked a label into a raster."""
    for name, ref in _static_refs():
        if "illustrations/" in ref:
            assert not re.search(r"[-_](en|sk|hu|uk)\.", ref), (
                f"{name} references a per-language illustration ({ref}); "
                "illustrations must be textless and shared"
            )
