from __future__ import annotations

import datetime as dt
import os
from zoneinfo import ZoneInfo

from playwright.sync_api import expect


def base_url() -> str:
    value = os.environ.get("CORVINUM_BASE_URL")
    if not value:
        raise RuntimeError("CORVINUM_BASE_URL must point to the CorvinumEU app container.")
    return value.rstrip("/")


def _login(page, local_part: str) -> None:
    page.goto(f"{base_url()}/prihlasenie/")
    page.fill("input[name='email']", f"{local_part}@demo.corvinum.test")
    page.fill("input[name='password']", "demo-corvinum-2026")
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")


def _login_recruiter(page) -> None:
    _login(page, "recruiter")


def test_corvinum_anonymous_authentication_is_client_branded(page):
    page.goto(f"{base_url()}/sk/prihlasenie/")

    expect(page.get_by_role("heading", name="Prihlásenie — CorvinumEU PeopleOps")).to_be_visible()
    logo_src = page.locator(".auth-brand-logo").get_attribute("src")
    assert logo_src is not None
    assert "/static/corvinum/brand/corvinum-logo-v1." in logo_src
    assert logo_src.endswith(".webp")
    assert "jober" not in page.content().lower()
    assert "Jober" not in page.title()


def test_corvinum_brand_and_content_use_available_viewport(page):
    page.set_viewport_size({"width": 1650, "height": 900})
    _login_recruiter(page)
    page.goto(f"{base_url()}/hu/people/")
    page.wait_for_load_state("networkidle")

    desktop = page.evaluate("""
      () => {
        const sidebar = document.querySelector('.sidebar').getBoundingClientRect();
        const main = document.querySelector('.cv-main').getBoundingClientRect();
        const brand = document.querySelector('.brand-word').getBoundingClientRect();
        return {
          sidebarRight: sidebar.right,
          sidebarWidth: sidebar.width,
          mainCenter: main.left + main.width / 2,
          expectedCenter: sidebar.right + (innerWidth - sidebar.right) / 2,
          brandRight: brand.right,
          brandText: document.querySelector('.brand-word').textContent.trim(),
          overflow: document.documentElement.scrollWidth - innerWidth,
        };
      }
    """)
    assert desktop["sidebarWidth"] == 280
    assert desktop["brandText"] == "CorvinumEU PeopleOps"
    assert desktop["brandRight"] <= desktop["sidebarRight"] - 12
    assert abs(desktop["mainCenter"] - desktop["expectedCenter"]) <= 1
    assert desktop["overflow"] == 0

    page.locator("[data-nav-toggle]").click()
    page.wait_for_timeout(450)
    rail = page.evaluate("""
      () => {
        const sidebar = document.querySelector('.sidebar').getBoundingClientRect();
        const main = document.querySelector('.cv-main').getBoundingClientRect();
        return {
          sidebarWidth: sidebar.width,
          mainCenter: main.left + main.width / 2,
          expectedCenter: sidebar.right + (innerWidth - sidebar.right) / 2,
        };
      }
    """)
    assert rail["sidebarWidth"] == 72
    assert abs(rail["mainCenter"] - rail["expectedCenter"]) <= 1

    page.set_viewport_size({"width": 375, "height": 667})
    page.reload()
    page.wait_for_load_state("networkidle")
    mobile = page.evaluate("""
      () => {
        const main = document.querySelector('.cv-main').getBoundingClientRect();
        return {
          left: main.left,
          right: main.right,
          overflow: document.documentElement.scrollWidth - innerWidth,
        };
      }
    """)
    assert mobile == {"left": 0, "right": 375, "overflow": 0}


def test_corvinum_language_switch_uses_its_own_cookie_and_translates_the_url(page):
    _login_recruiter(page)
    page.goto(f"{base_url()}/sk/people/")
    page.select_option(".sb-actions select[name='language']", "hu")
    page.wait_for_url("**/hu/people/")

    assert page.locator("html").get_attribute("lang") == "hu"
    cookies = {cookie["name"]: cookie["value"] for cookie in page.context.cookies()}
    assert cookies["corvinum_language"] == "hu"


def test_corvinum_reports_are_the_interactive_overview(page):
    _login_recruiter(page)
    page.goto(f"{base_url()}/sk/reports/")
    page.wait_for_load_state("networkidle")

    assert "Prehľad" not in page.locator(".sb-nav .sb-text").all_text_contents()
    assert page.locator("a.metric-card[href*='/projects/']").count() == 1
    assert page.locator("a.metric-card[href*='/people/']").count() == 1
    assert page.locator(".detail-grid a[href*='/people/?status=available']").count() == 1

    page.locator("a.metric-card[href*='/people/']").click()
    page.wait_for_url("**/sk/people/")


def test_corvinum_person_edit_includes_email(page):
    _login_recruiter(page)
    page.goto(f"{base_url()}/sk/people/")
    page.locator("main a[href*='/people/']").first.click()
    page.locator("a[href$='/edit/']").click()
    page.locator("input[name='email']").wait_for()


def test_corvinum_notification_center_uses_shared_responsive_panel(page):
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page, "coordinator")
    center = page.locator("#notification-center")
    center.wait_for()
    center.locator(".notification-toggle").click()
    popover = center.locator(".notification-popover")
    expect(popover).to_be_visible()
    box = popover.bounding_box()
    assert box is not None
    assert box["x"] >= 0
    assert box["x"] + box["width"] <= 375
    assert page.evaluate("document.documentElement.scrollWidth") == 375


def test_corvinum_audit_table_keeps_columns_inside_a_scroll_panel(page):
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page, "observer")
    page.goto(f"{base_url()}/sk/audit/")
    page.wait_for_load_state("networkidle")

    wrapper = page.locator(".data-table-scroll")
    table = wrapper.locator(".audit-table")
    expect(wrapper).to_be_visible()
    expect(table.locator("thead th")).to_have_count(5)
    expect(table.locator("tbody tr").first.locator("td")).to_have_count(5)

    layout = page.evaluate("""
      () => {
        const wrapper = document.querySelector('.data-table-scroll');
        const row = document.querySelector('.audit-table tbody tr');
        const cells = [...row.cells];
        return {
          documentWidth: document.documentElement.scrollWidth,
          viewportWidth: innerWidth,
          wrapperClientWidth: wrapper.clientWidth,
          wrapperScrollWidth: wrapper.scrollWidth,
          overflowX: getComputedStyle(wrapper).overflowX,
          timestampWhiteSpace: getComputedStyle(cells[0]).whiteSpace,
          cellLefts: cells.map(cell => cell.offsetLeft),
        };
      }
    """)
    assert layout["documentWidth"] == layout["viewportWidth"]
    assert layout["wrapperScrollWidth"] > layout["wrapperClientWidth"]
    assert layout["overflowX"] == "auto"
    assert layout["timestampWhiteSpace"] == "nowrap"
    assert layout["cellLefts"] == sorted(layout["cellLefts"])


def test_corvinum_project_page_keeps_clean_layout_without_transport(page):
    page.set_viewport_size({"width": 1650, "height": 900})
    _login_recruiter(page)
    page.goto(f"{base_url()}/hu/projects/")
    page.wait_for_load_state("networkidle")
    page.locator("main a[href*='/projects/']").first.click()
    page.wait_for_load_state("networkidle")

    layout = page.evaluate("""
      () => {
        const overview = document.querySelector('.cv-main > .two-column').getBoundingClientRect();
        return {
          overviewWidth: overview.width,
          transportHeadings: [...document.querySelectorAll('h2')]
            .filter((heading) => heading.textContent.trim() === 'Szállítás').length,
          overflow: document.documentElement.scrollWidth - innerWidth,
        };
      }
    """)
    assert layout["overviewWidth"] > 0
    assert layout["transportHeadings"] == 0
    assert layout["overflow"] == 0


def test_corvinum_coordinator_can_tick_checklist_with_csrf(page):
    """A rendered checklist control must remain a normal CSRF-protected POST,
    rather than exposing a state-changing URL that only works by direct access.
    The htmx enhancement must update in place without losing the user's scroll
    position."""
    page.set_viewport_size({"width": 1280, "height": 667})
    _login(page, "coordinator")
    page.goto(f"{base_url()}/hu/people/")
    page.wait_for_load_state("networkidle")
    page.locator("main a[href*='/people/']").first.click()
    page.wait_for_load_state("networkidle")

    form = page.locator("form[action*='/checklist/'][action$='/toggle/']").first
    assert form.locator("input[name='csrfmiddlewaretoken']").count() == 1
    assert any(cookie["name"] == "corvinum_csrftoken" for cookie in page.context.cookies())  # per-client cookie names (session slice)
    form.scroll_into_view_if_needed()
    page.evaluate("window.scrollBy(0, -120)")
    scroll_before = page.evaluate("window.scrollY")
    page_url = page.url
    form.locator("button[type='submit']").click()
    expect(page.locator("#activation-checklist")).to_contain_text("coordinator@demo.corvinum.test")

    assert page.url == page_url
    assert abs(page.evaluate("window.scrollY") - scroll_before) < 2
    assert "CSRF verification failed" not in page.content()


def test_corvinum_ledger_groups_controls_and_keeps_tables_aligned(page):
    page.set_viewport_size({"width": 1470, "height": 900})
    _login(page, "observer")
    today = dt.datetime.now(ZoneInfo("Europe/Bratislava")).date()
    cycle_month = today.month if today.day <= 20 else today.month % 12 + 1
    cycle_year = today.year + (1 if today.day > 20 and today.month == 12 else 0)
    page.goto(
        f"{base_url()}/hu/ledger/?year={cycle_year}&month={cycle_month}"
    )
    page.wait_for_load_state("networkidle")

    desktop = page.evaluate("""
      () => {
        const filter = document.querySelector('.ledger-cycle-filter');
        const inputs = [...filter.querySelectorAll('input')].map((input) => input.getBoundingClientRect());
        const button = filter.querySelector('button').getBoundingClientRect();
        const summary = document.querySelector('.ledger-cycle-summary').getBoundingClientRect();
        const entries = document.querySelector('.ledger-entries .ledger-table').getBoundingClientRect();
        const activity = document.querySelector('.ledger-activity-panel');
        const cyclePanel = document.querySelector('.ledger-cycle');
        return {
          display: getComputedStyle(filter).display,
          labels: filter.querySelectorAll('.field-mini').length,
          inputWidths: inputs.map((input) => input.width),
          aligned: inputs.every((input) => Math.abs(input.bottom - button.bottom) <= 1),
          summaryWidth: summary.width,
          entriesWidth: entries.width,
          summaryAndEntriesMerged: activity.contains(document.querySelector('.ledger-summary-table'))
            && activity.contains(document.querySelector('.ledger-entries')),
          entriesRemovedFromCycle: !cyclePanel.contains(document.querySelector('.ledger-entries')),
          overflow: document.documentElement.scrollWidth - innerWidth,
        };
      }
    """)
    assert desktop["display"] == "grid"
    assert desktop["labels"] == 2
    assert desktop["inputWidths"] == [192, 160]
    assert desktop["aligned"]
    assert desktop["summaryWidth"] == 832
    assert desktop["entriesWidth"] > desktop["summaryWidth"]
    assert desktop["summaryAndEntriesMerged"]
    assert desktop["entriesRemovedFromCycle"]
    assert desktop["overflow"] == 0

    page.set_viewport_size({"width": 375, "height": 667})
    page.reload()
    page.wait_for_load_state("networkidle")
    mobile = page.evaluate("""
      () => ({
        pageOverflow: document.documentElement.scrollWidth - innerWidth,
        entryScrolls: document.querySelector('.ledger-entries').scrollWidth > document.querySelector('.ledger-entries').clientWidth,
      })
    """)
    assert mobile == {"pageOverflow": 0, "entryScrolls": True}


def test_corvinum_wage_and_payslip_sources_are_aligned_and_responsive(page):
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page, "observer")

    page.goto(f"{base_url()}/sk/wages/")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Hrubé mzdy", exact=True)).to_be_visible()
    wage_table = page.locator(".data-table").last
    expect(wage_table).to_contain_text("2050,00")
    expect(wage_table).to_contain_text("1920,00")

    page.get_by_role("link", name="Eszter Varga").first.click()
    overview = page.locator("[data-testid='person-finance-overview']")
    expect(overview).to_be_visible()
    expect(overview.locator("thead th")).to_have_count(3)
    expect(overview).to_contain_text("2050,00")
    expect(overview).to_contain_text("1540,00")
    expect(overview).to_contain_text("1920,00")
    expect(overview).to_contain_text("1450,00")
    assert "Vypočítaná čistá mzda" not in overview.inner_text()

    layout = page.evaluate("""
      () => ({
        pageOverflow: document.documentElement.scrollWidth - innerWidth,
        overviewScrolls: document.querySelector(
          '[data-testid="person-finance-overview"] .data-table-scroll'
        ).scrollWidth > document.querySelector(
          '[data-testid="person-finance-overview"] .data-table-scroll'
        ).clientWidth,
      })
    """)
    assert layout == {"pageOverflow": 0, "overviewScrolls": True}

    page.goto(f"{base_url()}/sk/payslips/")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Výplatné pásky", exact=True)).to_be_visible()
    payslip_table = page.locator(".data-table").last
    expect(payslip_table.locator("thead th")).to_have_count(5)
    expect(payslip_table).to_contain_text("2026-07-20")
    expect(payslip_table).to_contain_text("2026-07-05")
    payslip_layout = page.evaluate("""
      () => ({
        pageOverflow: document.documentElement.scrollWidth - innerWidth,
        tableScrolls: document.querySelector(
          '.data-table-scroll'
        ).scrollWidth > document.querySelector(
          '.data-table-scroll'
        ).clientWidth,
      })
    """)
    assert payslip_layout == {"pageOverflow": 0, "tableScrolls": True}
