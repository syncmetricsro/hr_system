from __future__ import annotations

from playwright.sync_api import expect

from test_feature_pages import MANAGER, _login, base_url


def test_manager_operates_trials_warehouse_and_accommodation(page):
    _login(page, MANAGER)

    # Schedule an Available candidate from the central queue.
    page.goto(f"{base_url()}/en/trials/?create=1")
    form = page.locator("form[action*='/trials/create/']")
    expect(form).to_be_visible()
    candidate = form.locator("select[name='person'] option").filter(has_not_text="---------").first
    candidate_label = candidate.inner_text()
    form.locator("select[name='person']").select_option(candidate.get_attribute("value"))
    form.locator("select[name='project']").select_option(index=1)
    form.locator("input[name='scheduled_for']").fill("2030-01-07T08:30")
    form.locator("textarea[name='note']").fill("E2E main gate")
    form.get_by_role("button", name="Schedule trial").click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_text(candidate_label, exact=True)).to_be_visible()
    expect(page.get_by_text("E2E main gate", exact=True)).to_be_visible()

    # Receive a fictional lot and land on the current warehouse balance.
    page.goto(f"{base_url()}/en/equipment/stock/receive/")
    receipt = page.locator("main form")
    expect(receipt).to_be_visible()
    receipt.locator("input[name='received_on']").fill("2030-01-07")
    receipt.locator("input[name='reference']").fill("E2E-RECEIPT")
    receipt.locator("select[name='lines-0-item']").select_option(index=1)
    receipt.locator("input[name='lines-0-quantity']").fill("3")
    receipt.locator("input[name='lines-0-total_value']").fill("75.00")
    receipt.get_by_role("button", name="Record receipt").click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Warehouse stock")).to_be_visible()

    # Managers create catalogue records; the new room becomes visible on detail.
    page.goto(f"{base_url()}/en/accommodation/new/")
    page.locator("input[name='name']").fill("Residence E2E")
    page.locator("input[name='address']").fill("Fictional Street 1")
    page.locator("input[name='is_active']").check()
    page.get_by_role("button", name="Save location").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="Add room").click()
    page.locator("input[name='label']").fill("E2E-101")
    page.locator("input[name='capacity']").fill("3")
    page.locator("input[name='monthly_rate']").fill("250.00")
    page.locator("input[name='is_active']").check()
    page.get_by_role("button", name="Save room").click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="E2E-101")).to_be_visible()
    expect(page.get_by_text("250.00 EUR", exact=True)).to_be_visible()


def test_operations_forms_fit_mobile(page):
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page, MANAGER)
    for path, action in (
        ("/en/trials/?create=1", "/trials/create/"),
        ("/en/equipment/stock/receive/", "/equipment/stock/receive/"),
        ("/en/accommodation/new/", "/accommodation/new/"),
    ):
        page.goto(f"{base_url()}{path}")
        form = page.locator(f"form[action*='{action}']") if "?" in path else page.locator("main form")
        expect(form).to_be_visible()
        box = form.bounding_box()
        assert box is not None and box["x"] >= 0 and box["x"] + box["width"] <= 375
