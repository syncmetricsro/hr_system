from __future__ import annotations

import os

import pytest
from playwright.sync_api import expect


CLIENTS = (
    {
        "base_env": "BASE_URL",
        "language": "sk",
        "email": "manazer@demo.jober.test",
        "password": "demo-jober-2026",
    },
    {
        "base_env": "CORVINUM_BASE_URL",
        "language": "hu",
        "email": "recruiter@demo.corvinum.test",
        "password": "demo-corvinum-2026",
    },
)


def _login(page, client):
    base = os.environ[client["base_env"]].rstrip("/")
    language = client["language"]
    page.goto(f"{base}/{language}/prihlasenie/")
    page.fill("input[name='email']", client["email"])
    page.fill("input[name='password']", client["password"])
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")
    return base


def _contrast(page, selector: str) -> float:
    return page.locator(selector).first.evaluate(
        """element => {
          const parse = value => value.match(/[0-9.]+/g).slice(0, 3).map(Number);
          const linear = value => {
            value /= 255;
            return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
          };
          const luminance = color => {
            const [r, g, b] = parse(color).map(linear);
            return 0.2126 * r + 0.7152 * g + 0.0722 * b;
          };
          const style = getComputedStyle(element);
          const foreground = luminance(style.color);
          const background = luminance(style.backgroundColor);
          const high = Math.max(foreground, background);
          const low = Math.min(foreground, background);
          return (high + 0.05) / (low + 0.05);
        }"""
    )


def _assert_help_card_icons_fit_tiles(page) -> None:
    measurements = page.locator(".help-card-icon").evaluate_all(
        """tiles => tiles.map(tile => {
          const glyph = tile.querySelector(".icon");
          const tileBox = tile.getBoundingClientRect();
          const glyphBox = glyph.getBoundingClientRect();
          return {
            tile: {
              top: tileBox.top,
              right: tileBox.right,
              bottom: tileBox.bottom,
              left: tileBox.left,
            },
            glyph: {
              width: glyphBox.width,
              height: glyphBox.height,
              top: glyphBox.top,
              right: glyphBox.right,
              bottom: glyphBox.bottom,
              left: glyphBox.left,
            },
          };
        })"""
    )

    assert len(measurements) == 12
    for measurement in measurements:
        tile = measurement["tile"]
        glyph = measurement["glyph"]
        assert 23 <= glyph["width"] <= 25
        assert 23 <= glyph["height"] <= 25
        assert glyph["left"] >= tile["left"]
        assert glyph["right"] <= tile["right"]
        assert glyph["top"] >= tile["top"]
        assert glyph["bottom"] <= tile["bottom"]


@pytest.mark.parametrize("client_config", CLIENTS)
def test_help_cards_and_articles_work_on_desktop_and_mobile(page, client_config):
    page.set_viewport_size({"width": 1440, "height": 900})
    base = _login(page, client_config)
    language = client_config["language"]
    index_url = f"{base}/{language}/help/"
    page.goto(index_url)
    page.wait_for_load_state("networkidle")

    cards = page.locator("a.help-card")
    expect(cards).to_have_count(12)
    assert page.evaluate("document.documentElement.scrollWidth") == 1440
    _assert_help_card_icons_fit_tiles(page)

    workforce_cards = page.locator(".help-card-grid").nth(1).locator("a.help-card")
    expect(workforce_cards).to_have_count(3)
    first_row = [workforce_cards.nth(index).bounding_box() for index in range(3)]
    assert all(box is not None for box in first_row)
    assert max(box["y"] for box in first_row) - min(box["y"] for box in first_row) < 2

    images = cards.locator("img")
    expect(images).to_have_count(12)
    for index in range(images.count()):
        images.nth(index).scroll_into_view_if_needed()
        assert images.nth(index).evaluate(
            "image => image.complete && image.naturalWidth === 640 && image.naturalHeight === 360"
        )

    hrefs = cards.evaluate_all("links => links.map(link => link.href)")
    assert len(set(hrefs)) == 12
    for href in hrefs:
        assert page.request.get(href).status == 200

    cards.first.focus()
    page.keyboard.press("Enter")
    page.wait_for_url("**/help/*/")
    for anchor in ("purpose", "permissions", "workflow", "boundary", "example"):
        expect(page.locator(f"#{anchor}")).to_be_visible()
    figure = page.locator(".help-figure")
    expect(figure).to_be_visible()
    expect(figure.locator(".help-figure-marker")).to_have_count(2)
    assert figure.locator("img").evaluate(
        "image => image.complete && image.naturalWidth === 1280 && image.naturalHeight === 720"
    )

    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(index_url)
    page.wait_for_load_state("networkidle")
    assert page.evaluate("document.documentElement.scrollWidth") == 375
    first = page.locator("a.help-card").nth(0).bounding_box()
    second = page.locator("a.help-card").nth(1).bounding_box()
    assert first is not None and second is not None
    assert abs(first["x"] - second["x"]) < 2
    assert second["y"] > first["y"] + first["height"]
    assert first["width"] >= 44 and first["height"] >= 44
    page.locator("a.help-card").nth(1).click()
    page.wait_for_url("**/help/*/")
    expect(page.locator(".help-workflow")).to_be_visible()


@pytest.mark.parametrize("client_config", CLIENTS)
def test_help_cards_remain_legible_in_light_and_dark_themes(page, client_config):
    page.set_viewport_size({"width": 1440, "height": 900})
    base = _login(page, client_config)
    language = client_config["language"]
    page.goto(f"{base}/{language}/help/")
    page.wait_for_load_state("networkidle")

    for theme in ("light", "dark"):
        page.select_option("[data-theme-select]", theme)
        page.locator(f"html.theme-{theme}").wait_for()
        assert _contrast(page, ".help-card") >= 4.5
        expect(page.locator(".help-card-media img").first).to_be_visible()
