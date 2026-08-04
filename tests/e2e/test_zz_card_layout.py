"""Decision cards must not squeeze their own form or overflow the page.

From a bug report with screenshots of CorvinumEU's activation queue. The
desktop symptom was measured before any fix: the reason input rendered **99px
wide** at 1280px, because `.field-card` is a two-column grid and seven
templates give it *three* children — so the form wrapped into the first column,
which the details list had already squeezed. After the fix the same probe reads
320px.

Tested on **CorvinumEU** because that is where it was reported and where it
reproduces; the CSS is shared, so Jober is fixed by the same rule. The request
is created through the UI rather than seeded — neither browser stack seeds a
pending approval, so the queue is empty and every assertion here would pass
while proving nothing. That is why `cards` is asserted first.

Both this and `test_z_certificate_uploads` drive the same manager, and only the
first login to arrive is shown the 2FA enrolment secret. They therefore share
`corvinum_auth.login_manager`, which caches it — so neither test depends on
running before the other.

Raising the request as the manager also reproduces the reported case exactly:
the requester value carries a long email, its role label, and the "your own
request" marker (ADR 0031), which is the longest value on the card.
"""

from __future__ import annotations

from corvinum_auth import login_manager
from test_corvinum_shell import base_url

PROBE = """
() => {
  const card = document.querySelector('.field-card');
  const input = document.querySelector('.field-card input[type="text"]');
  // A value box rendered to the LEFT of its own label is the "spilled out of a
  // fixed, right-aligned track" symptom, stated as something measurable.
  let spilling = 0;
  document.querySelectorAll('.field-card dl > div').forEach((row) => {
    const dt = row.querySelector('dt');
    const dd = row.querySelector('dd');
    if (dt && dd && dd.getBoundingClientRect().left < dt.getBoundingClientRect().left) {
      spilling += 1;
    }
  });
  return {
    cards: document.querySelectorAll('.field-card').length,
    pageOverflow: document.documentElement.scrollWidth - innerWidth,
    inputWidth: input ? Math.round(input.getBoundingClientRect().width) : null,
    spilling,
  };
}
"""


def _login_manager(page) -> None:
    """The activation queue is manager-only, and managers here have 2FA
    enforced, so enrolling (or verifying, if another test enrolled first) is
    part of reaching the page at all."""
    login_manager(page, app_url=base_url())


def _raise_a_pending_request(page) -> None:
    """Waive the trial, complete readiness, request activation — all as one
    manager, which is what a single-administrator office does (ADR 0031)."""
    page.goto(f"{base_url()}/sk/people/")
    page.wait_for_load_state("networkidle")
    page.locator("main a[href*='/people/']").first.click()
    page.wait_for_load_state("networkidle")

    waive = page.locator("form[action*='waive-trial']")
    if waive.count():
        waive.locator("select[name='project']").select_option(index=0)
        waive.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

    readiness = page.locator("form[action*='/readiness/']")
    if readiness.count():
        for pillar in ("medical", "gear", "accommodation"):
            field = readiness.locator(f"select[name='{pillar}']")
            if field.count():
                field.select_option("complete")
        # Required alongside a complete Medical since 2026-08-05: a tick with no
        # date used to activate straight into an unclearable compliance alert.
        date = readiness.locator("input[name='entry_medical_date']")
        if date.count():
            date.fill("2026-07-01")
        readiness.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

    activate = page.locator("form[action*='/activate/']")
    if activate.count():
        activate.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")


def _probe(page, path, width, height):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{base_url()}{path}")
    page.wait_for_load_state("networkidle")
    return page.evaluate(PROBE)


def test_the_activation_card_fits_and_keeps_its_form_usable(page):
    """Set up once, measure at both widths: the phone and desktop symptoms are
    one root cause, and the setup cannot be repeated once the person has a
    request in flight."""
    _login_manager(page)
    _raise_a_pending_request(page)

    for width, height in ((375, 667), (1280, 800)):
        probe = _probe(page, "/sk/activations/", width, height)

        assert probe["cards"] >= 1, (
            f"no activation card rendered, so this proves nothing: {probe}"
        )
        assert probe["pageOverflow"] == 0, (
            f"page scrolls sideways at {width}px: {probe}"
        )
        assert probe["spilling"] == 0, (
            f"a value renders left of its label at {width}px: {probe}"
        )
        # Measured at 99px before the fix; 320px after. 200 sits clearly
        # between the two, so this fails again if the card ever re-collapses.
        assert probe["inputWidth"] >= 200, (
            f"reason input is {probe['inputWidth']}px at {width}px: {probe}"
        )


def test_the_decision_modifier_is_only_on_cards_that_act(page):
    """The fix stops overflow; it is not licence to restyle every list. Ledger
    and people use `.field-card` too and must keep their two-column layout."""
    _login_manager(page)

    for path in ("/sk/people/", "/sk/ledger/"):
        page.goto(f"{base_url()}{path}")
        page.wait_for_load_state("networkidle")
        cards = page.locator(".field-card")
        for index in range(cards.count()):
            classes = cards.nth(index).get_attribute("class") or ""
            assert "field-card-decision" not in classes, f"{path} card {index}"


def test_the_worker_rail_reserves_no_gutter_on_a_phone(page):
    """The rail's 20rem gutter must not apply where the rail floats.

    Reported from a phone: the ledger's heading wrapped one character per line.
    The cause was not the ledger at all - `.cv-main` had `padding-right: 320px`
    on a 375px viewport, leaving a 39px content box, so every block on every
    page collapsed to min-content.

    It survived a `@media (max-width: 1100px)` override because `:has()` carries
    the specificity of its argument and media queries add none, so
    `:has(.worker-rail:not([data-collapsed="true"]))` kept winning. It only
    appears while the rail is **expanded**, which is why it never showed up in a
    test that left it collapsed - so this expands it first.
    """
    _login_manager(page)
    page.set_viewport_size({"width": 375, "height": 812})
    page.goto(f"{base_url()}/sk/ledger/")
    page.wait_for_load_state("networkidle")

    rail = page.locator(".worker-rail")
    if not rail.count():
        return  # rail not mounted for this client/role; nothing to reserve
    if rail.get_attribute("data-collapsed") == "true":
        page.locator(".worker-rail-toggle").click()
        page.wait_for_timeout(150)
    assert page.locator(".worker-rail").get_attribute("data-collapsed") != "true"

    layout = page.evaluate("""
      () => {
        const main = document.querySelector('.cv-main');
        const head = document.querySelector('.page-head');
        return {
          paddingLeft: getComputedStyle(main).paddingLeft,
          paddingRight: getComputedStyle(main).paddingRight,
          contentWidth: Math.round(main.clientWidth
            - parseFloat(getComputedStyle(main).paddingLeft)
            - parseFloat(getComputedStyle(main).paddingRight)),
          headWidth: head ? Math.round(head.getBoundingClientRect().width) : null,
        };
      }
    """)

    # Not zero — the shell keeps its ordinary gutter. The point is that the
    # rail's 20rem is not *added* to it, so the two sides stay symmetric.
    assert layout["paddingRight"] == layout["paddingLeft"], (
        f"rail gutter still reserved: {layout}"
    )
    # 39px before the fix. Anything near the viewport width means the page is
    # usable; the exact number moves with the shell's own padding.
    assert layout["contentWidth"] > 300, (
        f"content box is {layout['contentWidth']}px: {layout}"
    )
    if layout["headWidth"] is not None:
        assert layout["headWidth"] > 300, (
            f"page head is {layout['headWidth']}px: {layout}"
        )
