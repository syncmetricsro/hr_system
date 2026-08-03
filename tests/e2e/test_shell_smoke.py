from __future__ import annotations

import os

# Fictional seed credentials created by `manage.py seed_demo`.
DEMO_EMAIL = "manazer@demo.jober.test"
DEMO_PASSWORD = "demo-jober-2026"


def base_url() -> str:
    value = os.environ.get("BASE_URL")
    if not value:
        raise RuntimeError(
            "BASE_URL must point to the app container for browser smoke tests."
        )
    return value.rstrip("/")


def _login(page) -> None:
    page.goto(f"{base_url()}/prihlasenie/")
    page.get_by_role("heading", name="Prihlásenie — Jober").wait_for()
    page.fill("input[name='email']", DEMO_EMAIL)
    page.fill("input[name='password']", DEMO_PASSWORD)
    page.get_by_role("button", name="Pokračovať").click()
    page.get_by_role("heading", name="Reporty", exact=True).wait_for()


def test_shell_renders_mobile(page):
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page)
    # Dashboard shows real operational metric cards.
    page.get_by_role("heading", name="Reporty", exact=True).wait_for()
    page.get_by_text("Aktívne projekty").wait_for()


def test_person_panels_keep_clearance_in_both_themes(page):
    _login(page)
    page.goto(f"{base_url()}/en/people/1/")
    page.locator(".two-column").wait_for()

    def section_gap() -> float:
        return page.locator(".two-column").evaluate(
            """grid => {
              const next = grid.nextElementSibling;
              if (!next) throw new Error("Expected a panel after the person detail grid");
              return next.getBoundingClientRect().top - grid.getBoundingClientRect().bottom;
            }"""
        )

    for theme in ("light", "dark"):
        page.evaluate(
            """theme => {
              document.documentElement.classList.remove("theme-light", "theme-dark");
              document.documentElement.classList.add(`theme-${theme}`);
            }""",
            theme,
        )
        assert section_gap() >= 16

    page.set_viewport_size({"width": 375, "height": 667})
    assert section_gap() >= 16


def test_health_endpoint(page):
    page.goto(f"{base_url()}/healthz/")
    assert page.locator("body").inner_text() == "ok"


def test_login_page_renders(page):
    page.goto(f"{base_url()}/prihlasenie/")
    page.get_by_role("heading", name="Prihlásenie — Jober").wait_for()
    assert "corvinum" not in page.content().lower()
    assert "/static/jober/brand/jober-logo" in page.locator(
        ".auth-brand-logo"
    ).get_attribute("src")


def test_dashboard_requires_login(page):
    # Hitting the app root unauthenticated must bounce to the login screen.
    page.goto(f"{base_url()}/")
    page.get_by_role("heading", name="Prihlásenie — Jober").wait_for()


def test_static_css_is_served(page):
    # Regression: the production image must serve collected static files (via
    # WhiteNoise) with the correct content type, not the HTML 404 page.
    page.goto(f"{base_url()}/prihlasenie/")
    href = page.locator("link[rel='stylesheet']").first.get_attribute("href")
    response = page.request.get(f"{base_url()}{href}")
    assert response.status == 200
    assert "text/css" in response.headers["content-type"]


def test_language_switch_translates_a_mismatched_url_prefix(page):
    _login(page)
    page.goto(f"{base_url()}/hu/")
    assert page.locator("html").get_attribute("lang") == "hu"

    page.select_option(".language-switch select[name='language']", "en")
    page.wait_for_url("**/en/")

    assert page.locator("html").get_attribute("lang") == "en"
    assert (
        page.locator(".language-switch select[name='language']").input_value() == "en"
    )
    cookies = {cookie["name"]: cookie["value"] for cookie in page.context.cookies()}
    assert cookies["jober_language"] == "en"


# The three pages that embed the shared reporting-period picker, plus a few
# with their own filter forms and page-head actions for contrast.
SPACED_PAGES = (
    "/en/equipment/stock/",
    "/en/equipment/receipts/",
    "/en/staff-activity/",
    "/en/equipment/catalog/",
    "/en/equipment/reviews/",
    "/en/finance/",
    "/en/accommodation/costs/",
    "/en/blacklist/",
    "/en/activations/",
)

#: Below this a control reads as welded to whatever follows it.
MIN_BUTTON_GAP_PX = 12


def _button_gaps(page):
    """Gap from each button to the nearest thing rendered directly beneath it.

    Two details decide whether this measures anything real. It compares against
    the nearest element *anywhere* below rather than only top-level blocks —
    the defect this was written for is a button and a caption inside the same
    panel, which a top-level comparison steps straight over. And it ignores the
    button's own ancestors, because `.page-head` supplies its separation with
    `padding-bottom`, which sits inside its box and would otherwise read as a
    zero gap on correct markup.
    """
    return page.evaluate(
        """
        () => {
          const out = [];
          for (const btn of document.querySelectorAll('.app-shell button, .app-shell a.button')) {
            const b = btn.getBoundingClientRect();
            if (!b.width || !b.height) continue;
            let top = null, who = null;
            for (const el of document.querySelectorAll('.app-shell *')) {
              if (el.contains(btn) || btn.contains(el)) continue;
              const r = el.getBoundingClientRect();
              if (!r.width || !r.height) continue;
              if (r.top < b.bottom - 1) continue;            // not below
              if (r.right < b.left || r.left > b.right) continue;  // not in its column
              if (top === null || r.top < top) {
                top = r.top;
                who = el.tagName.toLowerCase() + '.' + (el.className || '').split(' ')[0];
              }
            }
            if (top === null) continue;
            out.push({
              label: (btn.innerText || btn.getAttribute('aria-label') || '?').trim().slice(0, 24),
              next: who,
              gap: Math.round(top - b.bottom),
            });
          }
          return out;
        }
        """
    )


def test_buttons_keep_clearance_from_what_follows_them(page):
    """A button must not sit hard against the next thing on the page.

    `.period-filter` shipped with no CSS at all, so the shared reporting-period
    picker rendered as raw block flow and its Filter button touched the caption
    beneath it — a measured **0px** on the warehouse stock, goods receipts and
    staff activity pages.

    Checked at two widths because wrapping changes what ends up adjacent, and
    across a wider page set than the two that were reported: the reporter said
    they had probably not found every instance, so the sweep is the answer to
    that rather than a spot check.
    """
    page.set_viewport_size({"width": 1280, "height": 900})
    _login(page)

    offenders = []
    for width in (1280, 375):
        page.set_viewport_size({"width": width, "height": 900})
        for path in SPACED_PAGES:
            page.goto(f"{base_url()}{path}")
            page.wait_for_load_state("networkidle")
            for row in _button_gaps(page):
                if row["gap"] < MIN_BUTTON_GAP_PX:
                    offenders.append(
                        f"{width}px {path} [{row['label']}] -> {row['next']} "
                        f"gap={row['gap']}px"
                    )

    assert not offenders, "buttons crowd what follows them:\n  " + "\n  ".join(
        offenders
    )
