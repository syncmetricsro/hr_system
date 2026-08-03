"""The offer-email surfaces render and gate correctly in a real browser.

Unit tests already pin the permissions and the office boundary. What only a
browser catches is the composition: a panel registered but never rendered, a
nav tab pointing at a URL the role cannot open, or a Send button that is
enabled when the recipient is opted out — the gap between "the view refuses"
and "the page never offered".
"""

from __future__ import annotations

from playwright.sync_api import expect

from test_feature_pages import MANAGER, OBSERVER, RECRUITER, _login, base_url


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


def test_the_bulk_send_page_previews_before_it_sends(page):
    """The confirm step is the whole point of the page: a manager should see
    the recipient list and a rendered body before anything leaves."""
    _login(page, MANAGER)
    page.goto(f"{base_url()}/en/offers/")
    page.locator("a[href*='/send/']").first.click()
    page.wait_for_load_state("networkidle")

    expect(page.locator("input[name='confirm']")).to_have_count(1)
    expect(page.get_by_text("recipient", exact=False).first).to_be_visible()


def test_an_observer_cannot_reach_the_offer_pages(page):
    """Observer spans every office by role bypass, which makes it exactly the
    account that must not be able to email anyone."""
    _login(page, OBSERVER)
    assert page.goto(f"{base_url()}/en/offers/").status == 403
