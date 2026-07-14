from __future__ import annotations

import os


def jober_url() -> str:
    return os.environ["BASE_URL"].rstrip("/")


def corvinum_url() -> str:
    return os.environ["CORVINUM_BASE_URL"].rstrip("/")


def _resolved(page) -> str:
    return page.locator("html").get_attribute("data-theme-resolved")


def test_jober_theme_default_logo_persistence_and_live_system_mode(page):
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{jober_url()}/prihlasenie/")
    page.evaluate("localStorage.removeItem('jober-theme')")
    page.reload()

    assert _resolved(page) == "light"
    logo = page.locator("img.brand-logo")
    assert logo.get_attribute("alt") == ""
    box = logo.bounding_box()
    assert box is not None
    assert 2.4 < box["width"] / box["height"] < 2.7

    page.select_option("[data-theme-select]", "dark")
    assert _resolved(page) == "dark"
    assert page.evaluate("localStorage.getItem('jober-theme')") == "dark"
    page.reload()
    assert _resolved(page) == "dark"
    assert page.evaluate("document.documentElement.scrollWidth") == 375

    page.emulate_media(color_scheme="dark")
    page.select_option("[data-theme-select]", "system")
    assert _resolved(page) == "dark"
    page.emulate_media(color_scheme="light")
    page.locator("html.theme-light").wait_for()
    assert _resolved(page) == "light"

    page.fill("input[name='email']", "manazer@demo.jober.test")
    page.fill("input[name='password']", "demo-jober-2026")
    page.locator(".login-panel button[type='submit']").click()
    page.wait_for_load_state("networkidle")
    assert page.locator("[data-theme-select]").input_value() == "system"
    assert _resolved(page) == "light"


def test_corvinum_dark_default_light_mode_and_cross_tab_sync(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{corvinum_url()}/prihlasenie/")
    page.evaluate("localStorage.removeItem('corvinum-theme')")
    page.reload()
    assert _resolved(page) == "dark"

    page.select_option("[data-theme-select]", "light")
    assert _resolved(page) == "light"
    assert page.evaluate("localStorage.getItem('corvinum-theme')") == "light"

    second = page.context.new_page()
    second.goto(f"{corvinum_url()}/prihlasenie/")
    assert _resolved(second) == "light"
    second.select_option("[data-theme-select]", "dark")
    assert _resolved(page) == "dark"
    second.close()

    page.select_option("[data-theme-select]", "light")
    page.fill("input[name='email']", "recruiter@demo.corvinum.test")
    page.fill("input[name='password']", "demo-corvinum-2026")
    page.locator(".login-panel button[type='submit']").click()
    page.wait_for_load_state("networkidle")
    assert _resolved(page) == "light"
    assert page.locator(".sb-actions [data-theme-select]").input_value() == "light"

    panel_color = page.locator(".panel").first.evaluate("element => getComputedStyle(element).backgroundColor")
    assert panel_color in {"rgba(255, 255, 255, 0.9)", "rgba(255, 255, 255, 0.898)"}


def test_theme_storage_failure_falls_back_to_each_client_default(browser):
    context = browser.new_context()
    context.add_init_script("""
      Storage.prototype.getItem = function () { throw new Error('blocked'); };
      Storage.prototype.setItem = function () { throw new Error('blocked'); };
    """)
    page = context.new_page()

    page.goto(f"{jober_url()}/prihlasenie/")
    assert _resolved(page) == "light"
    page.select_option("[data-theme-select]", "dark")
    assert _resolved(page) == "dark"

    page.goto(f"{corvinum_url()}/prihlasenie/")
    assert _resolved(page) == "dark"
    context.close()
