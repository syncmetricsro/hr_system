from __future__ import annotations

import os


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


def test_corvinum_top_level_sections_have_vertical_rhythm(page):
    page.set_viewport_size({"width": 1650, "height": 900})
    _login_recruiter(page)
    page.goto(f"{base_url()}/hu/projects/")
    page.wait_for_load_state("networkidle")
    page.locator("main a[href*='/projects/']").first.click()
    page.wait_for_load_state("networkidle")

    gap = page.evaluate("""
      () => {
        const overview = document.querySelector('.cv-main > .two-column').getBoundingClientRect();
        const nextPanel = document.querySelector('.cv-main > section.panel').getBoundingClientRect();
        return nextPanel.top - overview.bottom;
      }
    """)
    assert gap == 16


def test_corvinum_coordinator_can_tick_checklist_with_csrf(page):
    """A rendered checklist control must remain a normal CSRF-protected POST,
    rather than exposing a state-changing URL that only works by direct access."""
    _login(page, "coordinator")
    page.goto(f"{base_url()}/hu/people/")
    page.wait_for_load_state("networkidle")
    page.locator("main a[href*='/people/']").first.click()
    page.wait_for_load_state("networkidle")

    form = page.locator("form[action*='/checklist/'][action$='/toggle/']").first
    assert form.locator("input[name='csrfmiddlewaretoken']").count() == 1
    assert any(cookie["name"] == "corvinum_csrftoken" for cookie in page.context.cookies())  # per-client cookie names (session slice)
    form.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")

    assert "/people/" in page.url
    assert "CSRF verification failed" not in page.content()


def test_corvinum_ledger_groups_controls_and_keeps_tables_aligned(page):
    page.set_viewport_size({"width": 1470, "height": 900})
    _login(page, "observer")
    page.goto(f"{base_url()}/hu/ledger/?year=2026&month=7")
    page.wait_for_load_state("networkidle")

    desktop = page.evaluate("""
      () => {
        const filter = document.querySelector('.ledger-cycle-filter');
        const inputs = [...filter.querySelectorAll('input')].map((input) => input.getBoundingClientRect());
        const button = filter.querySelector('button').getBoundingClientRect();
        const summary = document.querySelector('.ledger-cycle-summary').getBoundingClientRect();
        const entries = document.querySelector('.ledger-entries .ledger-table').getBoundingClientRect();
        return {
          display: getComputedStyle(filter).display,
          labels: filter.querySelectorAll('.field-mini').length,
          inputWidths: inputs.map((input) => input.width),
          aligned: inputs.every((input) => Math.abs(input.bottom - button.bottom) <= 1),
          summaryWidth: summary.width,
          entriesWidth: entries.width,
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
