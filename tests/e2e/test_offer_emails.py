"""The offer-email surfaces render and gate correctly in a real browser.

Unit tests already pin the permissions and the office boundary. What only a
browser catches is the composition: a panel registered but never rendered, a
nav tab pointing at a URL the role cannot open, or a Send button that is
enabled when the recipient is opted out — the gap between "the view refuses"
and "the page never offered".
"""

from __future__ import annotations

from playwright.sync_api import expect

from corvinum_auth import login_manager
from test_feature_pages import MANAGER, OBSERVER, RECRUITER, _login, base_url
from test_corvinum_shell import base_url as corvinum_base_url


def test_manager_sees_the_offers_area(page):
    _login(page, MANAGER)
    page.goto(f"{base_url()}/en/offers/")
    page.get_by_role("heading", name="Job offers", exact=True).wait_for()
    # The seed leaves at least one offer to send.
    expect(page.locator("a[href*='/offers/'][href$='/edit/']").first).to_be_visible()


def test_offers_tab_is_in_the_nav_for_a_manager(page):
    _login(page, MANAGER)
    page.goto(f"{base_url()}/en/")
    expect(page.locator("nav#primary-nav a[href*='/offers/']")).to_have_count(1)


def test_a_recruiter_gets_no_offers_tab_and_no_offers_page(page):
    """Recruiters send offers from a person's card; authoring and campaigns are
    a manager's job. A visible tab that 403s would read as a broken app."""
    _login(page, RECRUITER)
    page.goto(f"{base_url()}/en/")
    expect(page.locator("nav#primary-nav a[href*='/offers/']")).to_have_count(0)

    response = page.goto(f"{base_url()}/en/offers/")
    assert response.status == 403


def test_the_offer_panel_renders_on_a_person_card(page):
    _login(page, MANAGER)
    page.goto(f"{base_url()}/en/people/1/")
    page.wait_for_load_state("networkidle")
    panel = page.locator("section.panel:has-text('Email a job offer')")
    expect(panel).to_have_count(1)
    expect(panel.locator("select[name='offer']")).to_be_visible()
    expect(panel.locator("select[name='kind']")).to_be_visible()


def test_the_bulk_send_page_selects_previews_confirms_and_reports(page):
    """The confirm step is the whole point of the page: a manager should see
    the recipient list and a rendered body before anything leaves."""
    _login(page, MANAGER)
    # The committed Jober seed deliberately stores no contact emails. Add one
    # fictional address through the same edit form a Manager uses, while the
    # isolated e2e stack's console backend guarantees there is no provider send.
    page.goto(f"{base_url()}/en/people/1/edit/")
    page.fill("input[name='email']", "offer-browser@demo.jober.test")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")
    page.goto(f"{base_url()}/en/offers/")
    page.locator("a[href*='/send/']").first.click()
    page.wait_for_load_state("networkidle")

    eligible = page.locator("input[name='recipients']:not([disabled])")
    expect(eligible.first).to_be_visible()
    expect(eligible.first).not_to_be_checked()
    eligible.first.check()
    expect(page.locator("[x-text='selected.length']")).to_have_text("1")
    page.get_by_role("button", name="Review selected recipients").click()

    expect(page.locator("input[name='confirm']")).to_have_count(1)
    expect(page.get_by_text("selected recipient", exact=False).first).to_be_visible()
    page.locator("input[name='confirm']").check()
    page.get_by_role("button", name="Send to selected recipients").click()

    expect(page.get_by_role("heading", name="Recipient outcomes")).to_be_visible()
    expect(page.locator("table.data-table tbody tr")).to_have_count(1)


def test_corvinum_bulk_picker_keeps_disabled_contacts_readable_on_mobile(page):
    page.set_viewport_size({"width": 375, "height": 667})
    app_url = corvinum_base_url()
    login_manager(page, app_url=app_url)
    page.goto(f"{app_url}/hu/offers/")
    page.locator("a[href*='/send/']").first.click()
    page.wait_for_load_state("networkidle")

    enabled = page.locator("input[name='recipients']:not([disabled])")
    disabled_row = page.locator(".recipient-row-disabled").first
    expect(enabled).to_have_count(1)
    expect(enabled.first).not_to_be_checked()
    expect(disabled_row).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth") == 375
    for theme in ("light", "dark"):
        page.select_option("[data-theme-select]", theme)
        expect(disabled_row).to_be_visible()

    enabled.first.check()
    row_box = enabled.first.locator("xpath=ancestor::label").bounding_box()
    assert row_box is not None and row_box["height"] >= 44
    page.locator("form.recipient-picker button[type='submit']").click()
    expect(page.locator("input[name='confirm']")).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth") == 375


def test_an_observer_cannot_reach_the_offer_pages(page):
    """Observer spans every office by role bypass, which makes it exactly the
    account that must not be able to email anyone."""
    _login(page, OBSERVER)
    assert page.goto(f"{base_url()}/en/offers/").status == 403
