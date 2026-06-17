from __future__ import annotations

import os


def base_url() -> str:
    value = os.environ.get("BASE_URL")
    if not value:
        raise RuntimeError("BASE_URL must point to the app container for browser smoke tests.")
    return value.rstrip("/")


def test_shell_renders_mobile(page):
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{base_url()}/")
    page.get_by_role("heading", name="Prevádzkový prehľad").wait_for()
    page.get_by_role("link", name="Načítať rad").click()
    page.get_by_text("DHL Bratislava").wait_for()


def test_health_endpoint(page):
    page.goto(f"{base_url()}/healthz/")
    assert page.locator("body").inner_text() == "ok"


def test_login_page_renders(page):
    page.goto(f"{base_url()}/prihlasenie/")
    page.get_by_role("heading", name="Prihlásenie tímu Jober").wait_for()
