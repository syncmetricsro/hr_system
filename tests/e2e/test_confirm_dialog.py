from __future__ import annotations

from playwright.sync_api import expect

from test_feature_pages import COORDINATOR, _login, base_url


def test_destructive_action_requires_confirmation(page):
    """Owner requirement (2026-07-11): destructive actions open a modal that
    describes the action; dismissing keeps state, Agree performs it. Selectors
    are language-independent (the UI runs under the Slovak default)."""
    _login(page, COORDINATOR)
    page.goto(f"{base_url()}/people/1/")
    page.wait_for_load_state("networkidle")

    exit_form = "form:has(input[name='outcome'][value='available'])"
    exit_button = page.locator(f"{exit_form} button[type='submit']")
    dialog = page.locator("#confirm-dialog")
    expect(exit_button).to_have_count(1)

    # Escape and Cancel both dismiss the modal without performing the action.
    exit_button.click()
    expect(dialog).to_be_visible()
    assert page.locator("#confirm-dialog-message").inner_text().strip()
    expect(page.locator("[data-confirm-cancel]")).to_be_focused()
    page.keyboard.press("Escape")
    expect(dialog).to_be_hidden()
    expect(exit_button).to_have_count(1)

    exit_button.click()
    expect(dialog).to_be_visible()
    page.locator("[data-confirm-cancel]").click()
    expect(dialog).to_be_hidden()
    expect(exit_button).to_have_count(1)

    # Agree path: the action goes through; the exit forms are gone afterwards.
    exit_button.click()
    expect(dialog).to_be_visible()
    page.locator("[data-confirm-agree]").click()
    page.wait_for_load_state("networkidle")
    page.goto(f"{base_url()}/people/1/")
    expect(page.locator(exit_form)).to_have_count(0)


def test_confirmation_preserves_validation_and_clicked_submitter(page):
    """The shared handler works for button-level messages, leaves native form
    validation in charge, and resubmits with the exact button the user chose."""
    page.set_viewport_size({"width": 375, "height": 667})
    _login(page, COORDINATOR)
    page.goto(f"{base_url()}/")
    page.evaluate("""
      window.confirmedSubmitter = null;
      const form = document.createElement("form");
      form.id = "confirmation-contract-form";
      form.innerHTML = `
        <input name="reason" required aria-label="Reason">
        <button type="submit" name="decision" value="first" data-confirm="First action message">First</button>
        <button type="submit" name="decision" value="second" data-confirm="Second action message">Second</button>
      `;
      form.addEventListener("submit", (event) => {
        if (!event.defaultPrevented) {
          event.preventDefault();
          window.confirmedSubmitter = event.submitter.value;
        }
      });
      document.querySelector("main").appendChild(form);
    """)

    dialog = page.locator("#confirm-dialog")
    page.get_by_role("button", name="First", exact=True).click()
    expect(dialog).to_be_hidden()  # the required field blocks submission first

    page.get_by_role("textbox", name="Reason").fill("checked")
    page.get_by_role("button", name="First", exact=True).click()
    expect(dialog).to_be_visible()
    expect(page.locator("#confirm-dialog-message")).to_have_text("First action message")
    assert page.locator(".confirm-dialog-actions").evaluate(
        "element => getComputedStyle(element).flexDirection"
    ) == "column-reverse"
    page.keyboard.press("Escape")

    page.get_by_role("button", name="Second", exact=True).click()
    expect(page.locator("#confirm-dialog-message")).to_have_text("Second action message")
    page.locator("[data-confirm-agree]").click()
    expect(dialog).to_be_hidden()
    assert page.evaluate("window.confirmedSubmitter") == "second"
