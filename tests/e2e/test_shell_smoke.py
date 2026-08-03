from __future__ import annotations

import os

# Fictional seed credentials created by `manage.py seed_demo`.
DEMO_EMAIL = "manazer@demo.jober.test"
DEMO_PASSWORD = "demo-jober-2026"


def base_url() -> str:
    value = os.environ.get("BASE_URL")
    if not value:
        raise RuntimeError(
            "BASE_URL must point to the app container for browser smoke tests."
        )
    return value.rstrip("/")


def _login(page) -> None:
    page.goto(f"{base_url()}/prihlasenie/")
    page.get_by_role("heading", name="Prihlásenie — Jober").wait_for()
    page.fill("input[name='email']", DEMO_EMAIL)
    page.fill("input[name='password']", DEMO_PASSWORD)
    page.get_by_role("button", name="Pokračovať").click()
    page.get_by_role("heading", name="Reporty", exact=True).wait_for()


def test_shell_renders_mobile(page):
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page)
    # Dashboard shows real operational metric cards.
    page.get_by_role("heading", name="Reporty", exact=True).wait_for()
    page.get_by_text("Aktívne projekty").wait_for()


def test_person_panels_keep_clearance_in_both_themes(page):
    _login(page)
    page.goto(f"{base_url()}/en/people/1/")
    page.locator(".two-column").wait_for()

    def section_gap() -> float:
        return page.locator(".two-column").evaluate(
            """grid => {
              const next = grid.nextElementSibling;
              if (!next) throw new Error("Expected a panel after the person detail grid");
              return next.getBoundingClientRect().top - grid.getBoundingClientRect().bottom;
            }"""
        )

    for theme in ("light", "dark"):
        page.evaluate(
            """theme => {
              document.documentElement.classList.remove("theme-light", "theme-dark");
              document.documentElement.classList.add(`theme-${theme}`);
            }""",
            theme,
        )
        assert section_gap() >= 16

    page.set_viewport_size({"width": 375, "height": 667})
    assert section_gap() >= 16


def test_health_endpoint(page):
    page.goto(f"{base_url()}/healthz/")
    assert page.locator("body").inner_text() == "ok"


def test_login_page_renders(page):
    page.goto(f"{base_url()}/prihlasenie/")
    page.get_by_role("heading", name="Prihlásenie — Jober").wait_for()
    assert "corvinum" not in page.content().lower()
    assert "/static/jober/brand/jober-logo" in page.locator(
        ".auth-brand-logo"
    ).get_attribute("src")


def test_dashboard_requires_login(page):
    # Hitting the app root unauthenticated must bounce to the login screen.
    page.goto(f"{base_url()}/")
    page.get_by_role("heading", name="Prihlásenie — Jober").wait_for()


def test_static_css_is_served(page):
    # Regression: the production image must serve collected static files (via
    # WhiteNoise) with the correct content type, not the HTML 404 page.
    page.goto(f"{base_url()}/prihlasenie/")
    href = page.locator("link[rel='stylesheet']").first.get_attribute("href")
    response = page.request.get(f"{base_url()}{href}")
    assert response.status == 200
    assert "text/css" in response.headers["content-type"]


def test_language_switch_translates_a_mismatched_url_prefix(page):
    _login(page)
    page.goto(f"{base_url()}/hu/")
    assert page.locator("html").get_attribute("lang") == "hu"

    page.select_option(".language-switch select[name='language']", "en")
    page.wait_for_url("**/en/")

    assert page.locator("html").get_attribute("lang") == "en"
    assert (
        page.locator(".language-switch select[name='language']").input_value() == "en"
    )
    cookies = {cookie["name"]: cookie["value"] for cookie in page.context.cookies()}
    assert cookies["jober_language"] == "en"


def _header_geometry(page):
    return page.evaluate("""
      () => {
        const r = (sel) => {
          const b = document.querySelector(sel).getBoundingClientRect();
          return {left: b.left, right: b.right, top: b.top, bottom: b.bottom};
        };
        return {
          toggle: r('.app-header .icon-button.mobile-only'),
          bell: r('#notification-center .notification-toggle'),
          brand: r('.app-header .brand-lockup'),
          account: r('.app-header .header-account'),
          viewport: innerWidth,
        };
      }
    """)


def _overlaps(a, b):
    return (
        a["left"] < b["right"]
        and b["left"] < a["right"]
        and a["top"] < b["bottom"]
        and b["top"] < a["bottom"]
    )


def test_nav_toggle_is_not_covered_by_the_notification_bell(page):
    """The notification centre is `position: fixed` in the top-right corner on
    narrow screens with z-index 55, above the sticky header's 10. A nav toggle
    placed in that corner was not merely hidden behind the bell — the bell
    swallowed the tap, so the mobile menu could not be opened at all.

    Geometry rather than a screenshot, and checked at two widths because the
    clearance depends on how much room the brand leaves.
    """
    for width in (375, 320):
        page.set_viewport_size({"width": width, "height": 667})
        if width == 375:
            _login(page)
        else:
            page.reload()
            page.wait_for_load_state("networkidle")

        g = _header_geometry(page)
        assert not _overlaps(g["toggle"], g["bell"]), (
            f"nav toggle sits under the notification bell at {width}px: {g}"
        )
        assert not _overlaps(g["toggle"], g["brand"]), (
            f"nav toggle collides with the brand at {width}px: {g}"
        )
        # Taking the toggle out of flow must not drop it onto the account row.
        assert not _overlaps(g["toggle"], g["account"]), (
            f"nav toggle collides with the account row at {width}px: {g}"
        )
        # A hairline gap would pass the overlap check and still be untappable
        # next to a 44px target, so require real separation.
        assert g["bell"]["left"] - g["toggle"]["right"] >= 8, (
            f"nav toggle is too close to the bell at {width}px: {g}"
        )
        assert g["toggle"]["left"] >= 0 and g["toggle"]["right"] <= g["viewport"]


def test_nav_toggle_still_opens_the_menu_on_mobile(page):
    """Moving the control must not break it: the menu still opens, and it opens
    over the page rather than widening it."""
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page)

    nav = page.locator("#primary-nav")
    assert nav.is_visible() is False
    page.locator(".app-header .icon-button.mobile-only").click()
    nav.wait_for(state="visible")
    assert page.evaluate("document.documentElement.scrollWidth") == 375
