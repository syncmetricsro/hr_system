from __future__ import annotations

import os

# Fictional seed credentials created by `manage.py seed_demo`.
DEMO_EMAIL = "manazer@demo.jober.test"
DEMO_PASSWORD = "demo-jober-2026"


def base_url() -> str:
    value = os.environ.get("BASE_URL")
    if not value:
        raise RuntimeError("BASE_URL must point to the app container for browser smoke tests.")
    return value.rstrip("/")


def _login(page) -> None:
    page.goto(f"{base_url()}/prihlasenie/")
    page.get_by_role("heading", name="Prihlásenie tímu Jober").wait_for()
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


def test_health_endpoint(page):
    page.goto(f"{base_url()}/healthz/")
    assert page.locator("body").inner_text() == "ok"


def test_login_page_renders(page):
    page.goto(f"{base_url()}/prihlasenie/")
    page.get_by_role("heading", name="Prihlásenie tímu Jober").wait_for()


def test_dashboard_requires_login(page):
    # Hitting the app root unauthenticated must bounce to the login screen.
    page.goto(f"{base_url()}/")
    page.get_by_role("heading", name="Prihlásenie tímu Jober").wait_for()


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
    assert page.locator(".language-switch select[name='language']").input_value() == "en"
    cookies = {cookie["name"]: cookie["value"] for cookie in page.context.cookies()}
    assert cookies["jober_language"] == "en"
