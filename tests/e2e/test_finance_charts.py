from __future__ import annotations

import os

PASSWORD = "demo-jober-2026"
MANAGER = "manazer"


def base_url() -> str:
    value = os.environ.get("BASE_URL")
    if not value:
        raise RuntimeError("BASE_URL must point to the app container for browser tests.")
    return value.rstrip("/")


def _login(page, local_part: str = MANAGER) -> None:
    page.goto(f"{base_url()}/prihlasenie/")
    page.fill("input[name='email']", f"{local_part}@demo.jober.test")
    page.fill("input[name='password']", PASSWORD)
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")


def test_finance_summary_renders_all_three_chart_types(page):
    _login(page)
    page.goto(f"{base_url()}/en/finance/")
    page.wait_for_load_state("networkidle")
    page.locator('canvas[data-chart="trend"]').wait_for()
    page.locator('canvas[data-chart="gauge"]').wait_for()
    page.locator('canvas[data-chart="diverging"]').wait_for()
    # A live Chart.js instance is attached, not just an empty <canvas>.
    assert page.evaluate(
        "!!Chart.getChart(document.querySelector('canvas[data-chart=\"trend\"]'))"
    )


def test_finance_year_renders_trend_and_project_charts(page):
    _login(page)
    page.goto(f"{base_url()}/en/finance/")
    page.locator("a[href*='/finance/year/']").first.click()
    page.wait_for_load_state("networkidle")
    page.locator('canvas[data-chart="trend"]').wait_for()
    page.locator('canvas[data-chart="diverging"]').wait_for()


def test_finance_month_detail_renders_group_chart(page):
    _login(page)
    page.goto(f"{base_url()}/en/finance/")
    page.locator("a[href*='/finance/month/']").first.click()
    page.wait_for_load_state("networkidle")
    page.locator('canvas[data-chart="diverging"]').wait_for()


def test_reports_renders_headcount_chart(page):
    _login(page)
    page.goto(f"{base_url()}/en/")
    page.wait_for_load_state("networkidle")
    page.locator('canvas[data-chart="magnitude"]').wait_for()


def test_chart_colors_update_live_on_theme_toggle(page):
    _login(page)
    page.goto(f"{base_url()}/en/finance/")
    page.wait_for_load_state("networkidle")
    canvas = "document.querySelector('canvas[data-chart=\"trend\"]')"

    page.select_option("[data-theme-select]", "light")
    color_light = page.evaluate(f"Chart.getChart({canvas}).data.datasets[0].borderColor")

    page.select_option("[data-theme-select]", "dark")
    page.wait_for_timeout(100)  # destroy+rebuild happens synchronously on the event, but let paint settle
    color_dark = page.evaluate(f"Chart.getChart({canvas}).data.datasets[0].borderColor")

    assert color_light != color_dark
