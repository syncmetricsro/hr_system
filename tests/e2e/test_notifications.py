from __future__ import annotations

import os


def base_url() -> str:
    value = os.environ.get("BASE_URL")
    if not value:
        raise RuntimeError("BASE_URL must point to the Jober app container.")
    return value.rstrip("/")


def _login_manager(page) -> None:
    page.goto(f"{base_url()}/prihlasenie/")
    page.fill("input[name='email']", "manazer@demo.jober.test")
    page.fill("input[name='password']", "demo-jober-2026")
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")


def test_jober_notification_center_opens_links_dismisses_and_does_not_poll(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    _login_manager(page)
    page.goto(f"{base_url()}/en/reports/")
    center = page.locator("#notification-center")
    center.wait_for()

    notification_requests = []
    page.on("request", lambda request: notification_requests.append(request.url) if "/notifications/" in request.url else None)
    page.wait_for_timeout(1500)
    assert notification_requests == []

    # Create a real actionable condition through the browser. Cross-user
    # session-feed filtering is covered at the service/view level; this browser
    # scenario exercises the shared panel against the full HTTP stack.
    page.goto(f"{base_url()}/en/people/?status=available")
    page.locator("a.person-row").first.click()
    trial_form = page.locator("form[action$='/assign-trial/']")
    trial_form.locator("input[name='scheduled_for']").fill("2026-07-14T09:30")
    trial_form.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")

    center = page.locator("#notification-center")
    center.locator(".notification-toggle").click()
    popover = center.locator(".notification-popover")
    popover.wait_for(state="visible")
    first_item = popover.locator(".notification-item").filter(
        has=page.locator("input[name='key'][value^='trial-outcome:']")
    ).first
    assert first_item.locator("a.notification-link").get_attribute("href")

    # Manual refresh preserves a still-current notification.
    with page.expect_response(lambda response: "/notifications/" in response.url):
        center.locator("a[aria-label='Refresh notifications']").click()
    center = page.locator("#notification-center")
    center.locator(".notification-toggle").click()
    popover = center.locator(".notification-popover")
    popover.wait_for(state="visible")
    first_item = popover.locator(".notification-item").filter(
        has=page.locator("input[name='key'][value^='trial-outcome:']")
    ).first

    key = first_item.locator("input[name='key']").get_attribute("value")
    with page.expect_response(lambda response: "/notifications/dismiss/" in response.url):
        first_item.locator("button[type='submit']").click()
    page.locator(f'#notification-center input[name="key"][value="{key}"]').wait_for(state="detached")


def test_jober_notification_center_fits_phone_viewport(page):
    page.set_viewport_size({"width": 375, "height": 667})
    _login_manager(page)
    page.locator("#notification-center .notification-toggle").click()
    box = page.locator("#notification-center .notification-popover").bounding_box()
    assert box is not None
    assert box["x"] >= 0
    assert box["x"] + box["width"] <= 375
    assert page.evaluate("document.documentElement.scrollWidth") == 375
