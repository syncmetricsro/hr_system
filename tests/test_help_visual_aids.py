from __future__ import annotations

from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.template.loader import render_to_string
from django.utils import translation

from core.ui.help import available_articles

REPO = Path(__file__).resolve().parent.parent


def test_help_static_directory_is_copied_into_the_image():
    dockerfile = (REPO / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY static/help /app/static/help" in dockerfile


def test_every_declared_screenshot_and_thumbnail_is_discoverable():
    missing = []
    for article in available_articles():
        for path in [
            article["thumbnail"],
            *(s["path"] for s in article["screenshots"]),
        ]:
            if find(path) is None:
                missing.append(path)
    assert not missing, f"Help assets are not servable: {missing}"


def test_rendered_help_uses_only_the_running_clients_asset_namespace():
    html = render_to_string("pages/help_index.html", {"help_groups": []})
    assert f"/screens/{settings.HELP_ASSET_NAMESPACE}/" not in html

    html = render_to_string(
        "pages/help_index.html",
        {"help_groups": [{"label": "x", "articles": available_articles()}]},
    )
    own = f"/screens/{settings.HELP_ASSET_NAMESPACE}/"
    other = (
        "/screens/corvinum/"
        if settings.HELP_ASSET_NAMESPACE == "jober"
        else "/screens/jober/"
    )
    assert own in html
    assert other not in html


@pytest.mark.parametrize("language", ["sk", "hu", "uk"])
def test_screenshot_alt_and_callout_text_is_translatable(language):
    with translation.override(language):
        article = available_articles()[0]
        alt = str(article["screenshots"][0]["alt"])
        callout = str(article["screenshots"][0]["callouts"][0]["text"])
    assert alt
    assert callout
    if language in dict(settings.LANGUAGES):
        assert (
            alt
            != "The client-specific application shell with its main navigation and account controls."
        )
        assert callout != "Open a module from the client navigation."


def test_screenshot_readme_forbids_sensitive_capture_targets():
    readme = (REPO / "static" / "help" / "README.md").read_text(encoding="utf-8")
    readme = " ".join(readme.split())
    for term in ("TOTP", "password", "provider credentials", "logs", "fictional"):
        assert term in readme
