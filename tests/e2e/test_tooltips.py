from __future__ import annotations

import os

from playwright.sync_api import expect


def jober_url() -> str:
    return os.environ["BASE_URL"].rstrip("/")


def corvinum_url() -> str:
    return os.environ["CORVINUM_BASE_URL"].rstrip("/")


def _login_jober(page) -> None:
    page.goto(f"{jober_url()}/prihlasenie/")
    page.fill("input[name='email']", "manazer@demo.jober.test")
    page.fill("input[name='password']", "demo-jober-2026")
    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")


def test_shared_tooltip_hover_keyboard_dynamic_confirmation_and_touch(page):
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{jober_url()}/prihlasenie/")

    page.locator("button[aria-controls='primary-nav']").click()
    navigation = page.locator(".folder-tab").first
    tooltip = page.locator("#app-tooltip")
    navigation.hover()
    expect(tooltip).to_be_visible(timeout=1_200)
    expect(tooltip).to_have_text("Ľudia")

    box = tooltip.bounding_box()
    assert box is not None
    assert box["x"] >= 8
    assert box["x"] + box["width"] <= 375 - 8
    assert tooltip.get_attribute("data-side") in {"top", "bottom"}

    tooltip.hover()
    page.wait_for_timeout(200)
    expect(tooltip).to_be_visible()
    page.keyboard.press("Escape")
    expect(tooltip).to_be_hidden()

    navigation.focus()
    expect(tooltip).to_be_visible(timeout=500)
    assert "app-tooltip" in (navigation.get_attribute("aria-describedby") or "")
    page.keyboard.press("Escape")
    assert navigation.get_attribute("aria-describedby") is None

    page.evaluate(
        """
        () => {
          const button = document.createElement('button');
          button.type = 'button';
          button.textContent = 'Top edge';
          button.dataset.tooltip = 'Flips below';
          button.style.position = 'fixed';
          button.style.top = '1px';
          button.style.left = '1px';
          document.body.appendChild(button);
        }
        """
    )
    page.get_by_role("button", name="Top edge").focus()
    expect(tooltip).to_have_text("Flips below")
    assert tooltip.get_attribute("data-side") == "bottom"
    page.keyboard.press("Escape")

    page.evaluate(
        """
        () => {
          const form = document.createElement('form');
          form.dataset.confirm = 'This action is permanent.';
          const button = document.createElement('button');
          button.type = 'submit';
          button.textContent = 'Dynamic action';
          form.appendChild(button);
          document.body.appendChild(form);
        }
        """
    )
    dynamic = page.get_by_role("button", name="Dynamic action")
    dynamic.focus()
    expect(tooltip).to_have_text("This action is permanent.")
    dynamic.click()
    expect(page.locator("#confirm-dialog")).to_have_attribute("open", "")
    expect(page.locator("#confirm-dialog-message")).to_have_text("This action is permanent.")
    page.locator("[data-confirm-cancel]").click()

    page.evaluate(
        """
        () => {
          const button = document.createElement('button');
          button.type = 'button';
          button.textContent = 'Touch action';
          button.dataset.tooltip = 'Touch help';
          button.onclick = () => { window.touchActionRan = true; };
          document.body.appendChild(button);
          button.dispatchEvent(new PointerEvent('pointerdown', {
            bubbles: true, pointerType: 'touch'
          }));
          button.focus();
        }
        """
    )
    page.wait_for_timeout(200)
    expect(tooltip).to_be_hidden()
    page.get_by_role("button", name="Touch action").click()
    assert page.evaluate("window.touchActionRan") is True


def test_corvinum_tooltip_colors_follow_light_and_dark_modes(page):
    page.goto(f"{corvinum_url()}/prihlasenie/")
    page.evaluate("localStorage.removeItem('corvinum-theme')")
    page.reload()
    page.evaluate(
        """
        () => {
          const button = document.createElement('button');
          button.type = 'button';
          button.textContent = 'Tooltip target';
          button.dataset.tooltip = 'Theme-aware tooltip';
          button.style.position = 'fixed';
          button.style.left = '50%';
          button.style.top = '50%';
          document.body.appendChild(button);
        }
        """
    )
    target = page.get_by_role("button", name="Tooltip target")
    tooltip = page.locator("#app-tooltip")

    target.hover()
    expect(tooltip).to_be_visible(timeout=1_200)
    dark = tooltip.evaluate(
        "element => ({backgroundColor: getComputedStyle(element).backgroundColor, color: getComputedStyle(element).color})"
    )
    assert dark["backgroundColor"] == "rgba(15, 25, 42, 0.98)"
    assert dark["color"] == "rgb(226, 232, 240)"

    page.mouse.move(1, 1)
    expect(tooltip).to_be_hidden()
    page.select_option("[data-theme-select]", "light")
    target.hover()
    expect(tooltip).to_be_visible(timeout=1_200)
    light = tooltip.evaluate(
        "element => ({backgroundColor: getComputedStyle(element).backgroundColor, color: getComputedStyle(element).color})"
    )
    assert light["backgroundColor"] == "rgba(255, 255, 255, 0.98)"
    assert light["color"] == "rgb(7, 30, 39)"


def test_dashboard_tooltips_explain_and_open_filtered_drill_downs(page):
    _login_jober(page)
    page.goto(f"{jober_url()}/en/reports/")
    page.select_option("[data-theme-select]", "dark")

    active_projects = page.locator("a.metric-card", has_text="Active projects")
    active_projects.hover()
    tooltip = page.locator("#app-tooltip")
    expect(tooltip.locator("[data-tooltip-heading]")).to_have_text(
        "Review active projects"
    )
    expect(tooltip.locator("[data-tooltip-body]")).to_have_text(
        "Open active projects to review their coordinators and assignments."
    )
    dark_background = tooltip.evaluate(
        "element => getComputedStyle(element).backgroundColor"
    )
    assert dark_background == "rgb(41, 36, 53)"

    page.mouse.move(1, 1)
    expect(tooltip).to_be_hidden()
    page.select_option("[data-theme-select]", "light")
    active_projects.hover()
    expect(tooltip).to_be_visible(timeout=1_200)
    light_background = tooltip.evaluate(
        "element => getComputedStyle(element).backgroundColor"
    )
    assert light_background == "rgb(27, 36, 48)"

    active_projects.click()
    page.wait_for_url("**/en/projects/?status=active")
    expect(page.locator("select[name='status']")).to_have_value("active")

    page.goto(f"{jober_url()}/en/reports/")
    page.mouse.move(1, 1)
    reason = page.locator("a[href*='inactive_reason=']").first
    reason.focus()
    expect(tooltip.locator("[data-tooltip-heading]")).to_contain_text(
        "View inactive people:"
    )
    expect(tooltip.locator("[data-tooltip-body]")).to_have_text(
        "Open People filtered to this inactive reason."
    )
    href = reason.get_attribute("href")
    reason.click()
    page.wait_for_url(f"**{href}")
    expect(page.locator("select[name='status']")).to_have_value("inactive")
    expect(page.locator("select[name='inactive_reason']")).not_to_have_value("")
