from __future__ import annotations

from pathlib import Path

import pytest
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext


REPO = Path(__file__).resolve().parent.parent


@pytest.mark.jober_only
def test_shared_tooltip_is_rendered_once_and_navigation_is_annotated(client):
    body = client.get(reverse("login")).content.decode()

    assert body.count('id="app-tooltip"') == 1
    assert 'class="app-tooltip" role="tooltip" hidden' in body
    assert body.count("data-tooltip=") >= 7
    assert 'href="/sk/people/" data-tooltip=' in body
    assert 'href="/sk/reports/" data-tooltip=' in body


def test_tooltip_controller_contract_covers_accessibility_touch_and_htmx():
    source = (REPO / "static/src/js/app.js").read_text(encoding="utf-8")

    assert 'node.closest("[data-tooltip]")' in source
    assert "submitter.form.dataset.confirm" in source
    assert "aria-describedby" in source
    assert 'event.pointerType === "touch"' in source
    assert "suppressFocusUntil" in source
    assert "htmx:beforeSwap" in source
    assert "window.innerWidth - tooltipBox.width" in source
    assert "}, 450)" not in source  # the delay stays centralized at the call site
    assert "scheduleShow(target, 450)" in source


def test_contextual_surfaces_and_native_title_migration_are_declared():
    reports = (REPO / "templates/pages/reports.html").read_text(encoding="utf-8")
    people = (REPO / "templates/pages/people_list.html").read_text(encoding="utf-8")
    notifications = (REPO / "templates/notifications/panel.html").read_text(encoding="utf-8")
    corvinum = (
        REPO / "clients/corvinum_eu/templates/layouts/base.html"
    ).read_text(encoding="utf-8")

    assert reports.count("data-tooltip") >= 6
    assert 'person-row" href=' in people and "data-tooltip" in people
    assert 'title="{% trans' not in notifications
    assert notifications.count("data-tooltip") >= 5
    assert corvinum.count("data-tooltip") >= 9


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Details"),
        ("sk", "Podrobnosti"),
        ("hu", "Részletek"),
        ("uk", "Деталі"),
    ],
)
def test_tooltip_detail_label_is_translated(language, expected):
    with translation.override(language):
        assert gettext("Details") == expected


def test_tooltip_palettes_are_client_and_mode_specific():
    shared = (REPO / "static/src/css/app.css").read_text(encoding="utf-8")
    corvinum = (
        REPO / "clients/corvinum_eu/static/corvinum/theme.css"
    ).read_text(encoding="utf-8")

    assert shared.count("--tooltip-bg:") == 2
    assert "--tooltip-bg: #1b2430" in shared
    assert "--tooltip-bg: #292435" in shared
    assert corvinum.count("--tooltip-bg:") == 2
    assert "rgba(255, 255, 255, 0.98)" in corvinum
    assert "rgba(15, 25, 42, 0.98)" in corvinum
    assert "prefers-reduced-motion: reduce" in shared


def _luminance(color: str) -> float:
    values = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in values
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def test_tooltip_text_pairs_meet_wcag_aa_contrast():
    pairs = {
        "jober-light": ("#ffffff", "#1b2430"),
        "jober-dark": ("#f7f3ff", "#292435"),
        "corvinum-light": ("#071e27", "#ffffff"),
        "corvinum-dark": ("#e2e8f0", "#0f192a"),
    }
    for foreground, background in pairs.values():
        light, dark = sorted((_luminance(foreground), _luminance(background)), reverse=True)
        assert (light + 0.05) / (dark + 0.05) >= 4.5
