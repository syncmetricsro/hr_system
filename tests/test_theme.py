from __future__ import annotations

from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext


REPO = Path(__file__).resolve().parent.parent


@pytest.mark.jober_only
def test_jober_theme_contract_and_logo_are_rendered_on_login(client):
    response = client.get(reverse("login"))
    body = response.content.decode()

    assert settings.CLIENT_DEFAULT_THEME == "light"
    assert settings.CLIENT_THEME_STORAGE_KEY == "jober-theme"
    assert 'class="theme-light"' in body
    assert 'data-theme-default="light"' in body
    assert 'data-theme-storage-key="jober-theme"' in body
    assert 'src="/static/src/js/theme.js"' in body
    assert 'src="/static/jober/brand/jober-logo.svg"' in body
    assert 'class="brand-mark"' not in body
    assert body.count('data-theme-select') == 1


@pytest.mark.jober_only
def test_jober_navigation_uses_accessible_client_owned_icons(client):
    response = client.get(reverse("login"))
    body = response.content.decode()

    assert body.count('<symbol id="nav-icon-') == 14
    assert '<use href="#nav-icon-people"></use>' in body
    assert '<use href="#nav-icon-reports"></use>' in body
    assert '<svg class="nav-icon" aria-hidden="true">' in body
    assert "material-symbols-outlined" not in body


def test_shared_theme_controller_supports_system_and_storage_failures():
    source = (REPO / "static/src/js/theme.js").read_text(encoding="utf-8")

    assert 'matchMedia("(prefers-color-scheme: dark)")' in source
    assert 'window.addEventListener("storage"' in source
    assert 'media.addEventListener("change"' in source
    assert "window.localStorage.getItem(storageKey)" in source
    assert "window.localStorage.setItem(storageKey, value)" in source
    assert source.count("catch (_error)") == 2


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", ("Theme", "Light", "Dark", "System")),
        ("sk", ("Téma", "Svetlá", "Tmavá", "Systém")),
        ("hu", ("Téma", "Világos", "Sötét", "Rendszer")),
        ("uk", ("Тема", "Світла", "Темна", "Система")),
    ],
)
def test_theme_labels_are_translated(language, expected):
    with translation.override(language):
        assert tuple(gettext(value) for value in ("Theme", "Light", "Dark", "System")) == expected


def test_theme_palettes_define_accessible_semantic_modes():
    shared = (REPO / "static/src/css/app.css").read_text(encoding="utf-8")
    corvinum = (REPO / "clients/corvinum_eu/static/corvinum/theme.css").read_text(encoding="utf-8")

    assert ".theme-dark {" in shared
    assert "--body-background:" in shared
    assert ".brand-logo" in shared
    assert "hue-rotate(18deg)" in shared
    assert "saturate(0.58)" in shared
    assert corvinum.count(".theme-dark {") == 1
    assert "--surface: #f3faff" in corvinum
    assert "--surface: #050b14" in corvinum


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_primary_theme_text_tokens_meet_wcag_aa_contrast():
    palettes = {
        "jober-light": ("#ffffff", ["#1b2430", "#5b6b7e", "#2557a7", "#047857", "#b45309", "#b3261e"]),
        "jober-dark": ("#211e2b", ["#f7f3ff", "#b5acbf", "#c4a7ff", "#65d6ad", "#ffc56d", "#ff7c8f"]),
        "corvinum-light": ("#ffffff", ["#071e27", "#596675", "#005bbf", "#007a58", "#805b00", "#ba1a1a"]),
        # Composite of the translucent Corvinum panel over its dark surface.
        "corvinum-dark": ("#0b1220", ["#e2e8f0", "#94a3b8", "#4d9cff", "#00d091", "#fdbc13", "#fb5b63"]),
    }
    failures = {
        name: [color for color in colors if _contrast(color, background) < 4.5]
        for name, (background, colors) in palettes.items()
    }
    assert failures == {name: [] for name in palettes}
