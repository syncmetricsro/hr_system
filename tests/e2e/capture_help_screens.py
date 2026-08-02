"""Capture Help screenshots from both seeded demo stacks.

This is an explicit capture job, not part of the normal browser suite.  It
starts from a 1440x900 viewport, captures only fictional seeded pages, crops to
16:9, and writes a primary WebP plus matching card thumbnail.  Textual callouts
remain translated HTML in the Help article and are never baked into the image.
"""

from __future__ import annotations

import base64
import hmac
import os
import struct
import time
from hashlib import sha1
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageOps

OUT = Path(os.environ.get("HELP_SCREENS_DIR", "/app/static/help/screens"))
JOBER_PASSWORD = "demo-jober-2026"
CORVINUM_PASSWORD = "demo-corvinum-2026"

pytestmark = pytest.mark.skipif(
    not os.environ.get("E2E_PYTEST_ARGS", "").endswith("capture_help_screens.py"),
    reason="capture job, run via scripts/capture_help_screens.sh",
)


def _totp_at(secret: str, timestamp: int) -> str:
    key = base64.b32decode(secret, casefold=True)
    counter = timestamp // 30
    digest = hmac.new(key, struct.pack(">Q", counter), sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % 1_000_000).zfill(6)


def _login(page, *, app_url: str, language: str, email: str, password: str) -> None:
    page.goto(f"{app_url}/{language}/prihlasenie/")
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")
    if "/2fa/setup/" in page.url:
        # Enrollment is completed only so the seeded HR Admin can reach the
        # restricted Help subjects. This page is never captured.
        secret = page.locator(".detail-grid code").inner_text()
        page.fill("input[name='code']", _totp_at(secret, int(time.time())))
        page.locator("main form.stack button[type='submit']").click()
        page.wait_for_load_state("networkidle")


def _save_webps(page, *, namespace: str, slug: str) -> None:
    page.wait_for_load_state("networkidle")
    source = Image.open(BytesIO(page.screenshot(full_page=False))).convert("RGB")
    primary = ImageOps.fit(
        source,
        (1280, 720),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.44),
    )
    thumb = primary.resize((640, 360), Image.Resampling.LANCZOS)

    directory = OUT / namespace
    directory.mkdir(parents=True, exist_ok=True)
    primary_path = directory / f"{slug}.webp"
    thumb_path = directory / f"{slug}-thumb.webp"
    primary.save(primary_path, "WEBP", quality=84, method=6, exif=b"")
    thumb.save(thumb_path, "WEBP", quality=80, method=6, exif=b"")
    print(f"captured {primary_path} and {thumb_path}")


def _capture_routes(page, *, app_url: str, language: str, namespace: str, routes):
    for slug, route in routes:
        page.goto(f"{app_url}/{language}{route}")
        page.wait_for_load_state("networkidle")
        assert page.locator("main").count() == 1, f"No main content at {page.url}"
        if slug == "audit":
            # The article may explain Audit, but capture neither event rows nor
            # any other log contents. Heading and filters are sufficient.
            page.locator(".audit-table").evaluate("element => element.remove()")
        _save_webps(page, namespace=namespace, slug=slug)


@pytest.fixture
def desktop(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    return page


def test_capture_jober_help_screens(desktop):
    page = desktop
    app_url = os.environ["BASE_URL"].rstrip("/")
    _login(
        page,
        app_url=app_url,
        language="sk",
        email="manazer@demo.jober.test",
        password=JOBER_PASSWORD,
    )
    _capture_routes(
        page,
        app_url=app_url,
        language="sk",
        namespace="jober",
        routes=(
            ("getting-started", "/reports/"),
            ("people", "/people/"),
            ("projects", "/projects/"),
            ("readiness", "/activations/"),
            ("compliance", "/compliance/"),
            ("equipment", "/equipment/stock/"),
            ("accommodation", "/accommodation/"),
            ("reports", "/reports/"),
            ("finance", "/finance/"),
            ("feedback", "/feedback/"),
            ("blacklist", "/blacklist/"),
            ("audit", "/audit/"),
        ),
    )


def test_capture_corvinum_help_screens(desktop):
    page = desktop
    app_url = os.environ["CORVINUM_BASE_URL"].rstrip("/")
    _login(
        page,
        app_url=app_url,
        language="hu",
        email="hradmin@demo.corvinum.test",
        password=CORVINUM_PASSWORD,
    )
    _capture_routes(
        page,
        app_url=app_url,
        language="hu",
        namespace="corvinum",
        routes=(
            ("getting-started", "/reports/"),
            ("people", "/people/"),
            ("projects", "/projects/"),
            ("readiness", "/activations/"),
            ("compliance", "/compliance/"),
            ("equipment", "/equipment/catalog/"),
            ("reports", "/reports/"),
            ("ledger", "/ledger/"),
            ("payslips", "/payslips/"),
            ("gross-wages", "/wages/"),
            ("blacklist", "/blacklist/"),
            ("audit", "/audit/"),
        ),
    )
