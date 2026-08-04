from __future__ import annotations

import base64
import os
import re

from playwright.sync_api import expect

from corvinum_auth import login_manager


# A genuine two-pixel-square PNG. Browser tests generate upload bytes in
# memory, so no demo or production media is checked into the repository.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGO0iephYGBgYmBgYGBgAAANcgEmNt000gAAAABJRU5ErkJggg=="
)


def _login(page, *, app_url: str, email: str, password: str) -> None:
    """Delegates to the shared helper: managers here have 2FA enforced and only
    the first test to reach the setup screen ever sees the secret, so the
    enrolment has to be shared rather than repeated (see corvinum_auth)."""
    login_manager(page, app_url=app_url, email=email, password=password)


def _upload_front_and_back(page, *, app_url: str, language: str, category: str) -> None:
    page.goto(f"{app_url}/{language}/people/")
    page.locator("main a[href*='/people/']").first.click()
    page.locator("a[href*='/certificates/add/']").click()

    page.select_option("select[name='category']", category)
    page.fill("input[name='issuer']", "Fictional Training Centre")
    page.fill("input[name='certificate_number']", "DEMO-ONLY-001")
    page.fill("input[name='issue_date']", "2026-07-01")
    page.fill("input[name='expiry_date']", "2027-07-01")
    page.locator("input[name='front_upload']").set_input_files(
        {"name": "front.png", "mimeType": "image/png", "buffer": PNG_BYTES}
    )
    page.locator("input[name='back_upload']").set_input_files(
        {"name": "back.png", "mimeType": "image/png", "buffer": PNG_BYTES}
    )
    page.locator("main form.stack button[type='submit']").click()

    page.wait_for_url(f"**/{language}/people/*/")
    front = page.locator("a[href*='/media/certificates/'][href$='/document']").last
    back = page.locator("a[href*='/media/certificates/'][href$='/back']").last
    expect(front).to_be_visible()
    expect(back).to_be_visible()
    assert page.request.get(f"{app_url}{front.get_attribute('href')}").status == 200
    assert page.request.get(f"{app_url}{back.get_attribute('href')}").status == 200


def test_jober_can_upload_an_occupational_certificate_card(page):
    app_url = os.environ["BASE_URL"].rstrip("/")
    _login(
        page,
        app_url=app_url,
        email="manazer@demo.jober.test",
        password="demo-jober-2026",
    )
    _upload_front_and_back(page, app_url=app_url, language="en", category="FORKLIFT")


def test_corvinum_can_upload_the_same_occupational_certificate_card(page):
    app_url = os.environ["CORVINUM_BASE_URL"].rstrip("/")
    _login(
        page,
        app_url=app_url,
        email="hradmin@demo.corvinum.test",
        password="demo-corvinum-2026",
    )
    _upload_front_and_back(page, app_url=app_url, language="sk", category="CRANE")


def _fill_certificate_form(
    page, *, app_url: str, language: str, category: str, number: str
):
    """Go straight to the add form for the first seeded worker.

    Navigated by URL rather than clicked through the person page: by the time
    these run, earlier tests have already added certificates, and the person
    page is busy enough that "the first link that looks like a person" is not a
    reliable route to this form.
    """
    page.goto(f"{app_url}/{language}/people/")
    page.wait_for_load_state("networkidle")
    href = page.locator("main a[href*='/people/']").first.get_attribute("href")
    person_pk = re.search(r"/people/(\d+)/", href).group(1)
    page.goto(f"{app_url}/{language}/people/{person_pk}/certificates/add/")
    page.wait_for_load_state("networkidle")

    page.select_option("select[name='category']", category)
    page.fill("input[name='issuer']", "Fictional Training Centre")
    page.fill("input[name='certificate_number']", number)
    page.fill("input[name='issue_date']", "2026-07-01")
    page.fill("input[name='expiry_date']", "2027-07-01")
    page.locator("input[name='front_upload']").set_input_files(
        {"name": "front.png", "mimeType": "image/png", "buffer": PNG_BYTES}
    )
    return page.locator("main form.stack button[type='submit']")


def _count_create_posts(page):
    """Record every create POST the UI manages to send, and stop each one.

    Answered with 204 rather than let through or aborted, and each choice was
    forced by something that broke:

    * letting it through navigates to the person page, which carries four other
      `form.stack` panels, so the button locator re-resolves onto a different
      element;
    * delaying it with `time.sleep` inside a sync route handler blocks
      Playwright's own thread, so no assertion can run while it waits;
    * aborting it leaves Chromium showing a network-error page, so the form is
      gone before anything can be asserted about it.

    A 204 keeps the page exactly where it is, so the only thing measured is how
    many submissions the interface allowed - which is the reported bug.
    """
    posts = []

    def handler(route, request):
        if request.method == "POST":
            posts.append(request.url)
        route.fulfill(status=204, body="")

    page.route("**/certificates/add/", handler)
    return posts


def test_the_upload_button_locks_and_says_what_it_is_doing(page):
    """The visible half of the guard: while the POST is in flight the button
    stops accepting presses and the page says an upload is running."""
    app_url = os.environ["BASE_URL"].rstrip("/")
    _login(
        page,
        app_url=app_url,
        email="manazer@demo.jober.test",
        password="demo-jober-2026",
    )
    button = _fill_certificate_form(
        page,
        app_url=app_url,
        language="en",
        category="FORKLIFT",
        number="DEMO-BUSY-001",
    )
    notice = page.locator("main form.stack [data-busy-region]")

    assert button.is_enabled()
    assert not notice.is_visible()

    _count_create_posts(page)
    button.click(no_wait_after=True)

    expect(button).to_be_disabled(timeout=3000)
    expect(notice).to_be_visible(timeout=3000)


def test_a_second_press_sends_no_second_request(page):
    """The half that matters to the data. `Certificate` has no uniqueness
    constraint, so every POST the interface allows becomes another row."""
    app_url = os.environ["BASE_URL"].rstrip("/")
    _login(
        page,
        app_url=app_url,
        email="manazer@demo.jober.test",
        password="demo-jober-2026",
    )
    button = _fill_certificate_form(
        page,
        app_url=app_url,
        language="en",
        category="CRANE",
        number="DEMO-DOUBLE-002",
    )
    posts = _count_create_posts(page)

    # Three presses, as fast as the browser delivers them - what an impatient
    # operator does when nothing appears to happen. force=True because refusing
    # the press is the behaviour under test.
    for _ in range(3):
        button.click(no_wait_after=True, force=True)

    page.wait_for_timeout(500)
    assert len(posts) == 1, f"the interface sent {len(posts)} create requests, not 1"
