"""Capture the Help area's screenshots from the seeded demo stacks (J9).

Not a test - a capture job that happens to need a browser, run through the same
harness so it never drifts from the app the e2e suite drives. Invoke it with
`scripts/capture_help_screens.sh`, never as part of the normal suite.

Captured in Slovak, the default and the language most users see. The app's own
chrome is therefore in one language; the numbered callouts beside each figure
carry the explanation in the reader's language, which is why the illustrations
that accompany them must stay textless.

Each shot is cropped to the region under discussion rather than shipping a full
page: a full-page screenshot of a busy screen explains nothing.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

PASSWORD = "demo-jober-2026"
OUT = Path(os.environ.get("HELP_SCREENS_DIR", "/app/static/help/screens"))

pytestmark = pytest.mark.skipif(
    not os.environ.get("E2E_PYTEST_ARGS", "").endswith("capture_help_screens.py"),
    reason="capture job, run via scripts/capture_help_screens.sh",
)


def base_url() -> str:
    return os.environ["BASE_URL"].rstrip("/")


def _login(page, local_part: str) -> None:
    page.goto(f"{base_url()}/prihlasenie/")
    page.fill("input[name='email']", f"{local_part}@demo.jober.test")
    page.fill("input[name='password']", PASSWORD)
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")


def _shot(page, path: str, selector: str | None = None) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    page.wait_for_load_state("networkidle")
    if selector:
        page.locator(selector).first.screenshot(path=str(target))
    else:
        page.screenshot(path=str(target))
    print(f"captured {target}")


@pytest.fixture
def desktop(page):
    # 1440x900 at DPR 2 - the plan's capture rule, and wide enough that the
    # folder-tab navigation does not collapse.
    page.set_viewport_size({"width": 1440, "height": 900})
    return page


def test_capture_jober_screens(desktop):
    page = desktop
    _login(page, "manazer")

    page.goto(f"{base_url()}/")
    _shot(page, "jober/getting-started-shell.png", ".folder-tabs")

    page.goto(f"{base_url()}/people/")
    _shot(page, "jober/people-list.png", ".field-list, main")

    page.goto(f"{base_url()}/audit/")
    _shot(page, "jober/audit-log.png", "main")

    page.goto(f"{base_url()}/equipment/stock/")
    _shot(page, "jober/logistics-stock.png", "main")

    page.goto(f"{base_url()}/equipment/receipts/")
    _shot(page, "jober/logistics-receipts.png", "main")

    page.goto(f"{base_url()}/staff-activity/")
    _shot(page, "jober/staff-activity.png", "main")

    page.goto(f"{base_url()}/accommodation/costs/")
    _shot(page, "jober/accommodation-costs.png", "main")

    page.goto(f"{base_url()}/finance/")
    _shot(page, "jober/finance-summary.png", "main")
    _shot(page, "jober/finance-record-panel.png", ".finance-record-panel")
