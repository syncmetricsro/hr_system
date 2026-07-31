from __future__ import annotations

import base64
import hmac
import os
import struct
import time
from hashlib import sha1

from playwright.sync_api import expect


# A genuine two-pixel-square PNG. Browser tests generate upload bytes in
# memory, so no demo or production media is checked into the repository.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGO0iephYGBgYmBgYGBgAAANcgEmNt000gAAAABJRU5ErkJggg=="
)


def _totp_at(secret: str, timestamp: int) -> str:
    key = base64.b32decode(secret, casefold=True)
    counter = timestamp // 30
    digest = hmac.new(key, struct.pack(">Q", counter), sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % 1_000_000).zfill(6)


def _login(page, *, app_url: str, email: str, password: str) -> None:
    page.goto(f"{app_url}/prihlasenie/")
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")
    if "/2fa/setup/" in page.url:
        secret = page.locator(".detail-grid code").inner_text()
        page.fill("input[name='code']", _totp_at(secret, int(time.time())))
        page.locator("main form.stack button[type='submit']").click()
        page.wait_for_load_state("networkidle")


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
