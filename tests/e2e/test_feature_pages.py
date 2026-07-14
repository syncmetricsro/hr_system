from __future__ import annotations

import os

# Fictional seed accounts from `manage.py seed_demo` (one per role).
PASSWORD = "demo-jober-2026"
MANAGER = "manazer"
OBSERVER = "pozorovatel"
RECRUITER = "naborar"
COORDINATOR = "koordinator"


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


# Assertions use the English URL prefix (/en/...) so the app renders the English
# source strings deterministically rather than depending on translated wording.


# --- rendering: the pages shipped this sprint actually load in a browser -------

def test_finance_summary_and_month_detail(page):
    _login(page)
    page.goto(f"{base_url()}/en/finance/")
    page.get_by_role("heading", name="Finance", exact=True).wait_for()
    page.get_by_role("heading", name="Group breakdown").wait_for()
    page.get_by_role("heading", name="Per-project results").wait_for()
    # Drill into a seeded financial month.
    page.locator("a[href*='/finance/month/']").first.click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("heading", name="Line items").wait_for()


def test_finance_year_page(page):
    _login(page)
    page.goto(f"{base_url()}/en/finance/")
    page.locator("a[href*='/finance/year/']").first.click()
    page.wait_for_load_state("networkidle")
    # On the year page "Per-project results" is an eyebrow label, not a heading.
    page.get_by_text("Per-project results").first.wait_for()
    page.get_by_text("Financial months").first.wait_for()


def test_accommodation_cost_report(page):
    _login(page)
    page.goto(f"{base_url()}/en/accommodation/costs/")
    page.get_by_role("heading", name="Cost report").wait_for()
    page.get_by_text("Reporting only").wait_for()


def test_equipment_review_queue(page):
    _login(page)
    page.goto(f"{base_url()}/en/equipment/reviews/")
    page.get_by_role("heading", name="Equipment reviews").wait_for()


def test_blacklist_queue(page):
    _login(page)
    page.goto(f"{base_url()}/en/blacklist/")
    page.get_by_role("heading", name="Blacklist review").wait_for()


def test_reports_inactive_by_reason(page):
    _login(page)
    page.goto(f"{base_url()}/en/reports/")
    page.get_by_role("heading", name="Inactive by reason").wait_for()


# --- navigation gating: manager-only tabs are absent for lesser roles ----------

def test_manager_sees_reviews_tab(page):
    _login(page, MANAGER)
    page.goto(f"{base_url()}/en/")
    navigation = page.locator(".folder-tabs")
    assert navigation.get_by_role("link", name="Reviews").count() == 1
    assert navigation.get_by_role("link", name="Finance").count() == 1
    assert navigation.get_by_role("link", name="Blacklist").count() == 1


def test_coordinator_blocked_from_blacklist_queue(page):
    _login(page, COORDINATOR)
    response = page.goto(f"{base_url()}/en/blacklist/")
    assert response.status == 403


def test_observer_has_finance_but_not_reviews_tab(page):
    _login(page, OBSERVER)
    page.goto(f"{base_url()}/en/")
    # Observer can view finance summaries but not the equipment review queue.
    navigation = page.locator(".folder-tabs")
    assert navigation.get_by_role("link", name="Finance").count() == 1
    assert navigation.get_by_role("link", name="Reviews").count() == 0


# --- access gating: direct hits return 403 for unauthorized roles --------------

def test_recruiter_blocked_from_accommodation_costs(page):
    _login(page, RECRUITER)
    response = page.goto(f"{base_url()}/en/accommodation/costs/")
    assert response.status == 403


def test_coordinator_blocked_from_equipment_reviews(page):
    _login(page, COORDINATOR)
    response = page.goto(f"{base_url()}/en/equipment/reviews/")
    assert response.status == 403
