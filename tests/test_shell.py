from __future__ import annotations

from pathlib import Path

import pytest
from django.urls import reverse


REPO = Path(__file__).resolve().parent.parent


def test_production_templates_do_not_use_multiline_short_comments():
    """Django's {# ... #} syntax is single-line; multiline notes render as
    visible text. Longer comments must use the comment template tag."""
    template_roots = (REPO / "templates", REPO / "clients")
    offenders = []
    for root in template_roots:
        for path in root.rglob("*.html"):
            source = path.read_text(encoding="utf-8")
            cursor = 0
            while (start := source.find("{#", cursor)) != -1:
                end = source.find("#}", start + 2)
                if end == -1 or "\n" in source[start:end]:
                    offenders.append(str(path.relative_to(REPO)))
                    break
                cursor = end + 2

    assert offenders == [], "multiline {# ... #} comments: " + ", ".join(offenders)


def test_shared_page_templates_never_hardcode_a_client_identity():
    """Shared pages must receive identity from BRAND_NAME, never name a tenant."""
    offenders = []
    for path in (REPO / "templates/pages").rglob("*.html"):
        source = path.read_text(encoding="utf-8").lower()
        if "jober" in source or "corvinum" in source:
            offenders.append(str(path.relative_to(REPO)))

    assert offenders == [], (
        "client identity leaked into shared templates: " + ", ".join(offenders)
    )


def test_every_authentication_screen_uses_the_shared_brand_lockup():
    for name in ("login.html", "two_factor_setup.html", "two_factor_verify.html"):
        source = (REPO / "templates/pages" / name).read_text(encoding="utf-8")
        assert '{% include "partials/auth_brand.html" %}' in source
        assert "{{ BRAND_NAME }}" in source


def test_flash_notifications_are_timed_and_shared_by_both_client_shells():
    """Both shells must show the same flash stack, and it must stay readable.

    "Shared" used to mean the same markup pasted into each base.html, which is
    shared only until someone edits one. It is now a single partial that both
    include, so this checks the include on each side and the behaviour once, in
    the one place it lives.
    """
    for template in (
        REPO / "templates/layouts/base.html",
        REPO / "clients/corvinum_eu/templates/layouts/base.html",
    ):
        source = template.read_text(encoding="utf-8")
        assert '{% include "partials/flash_messages.html" %}' in source
        assert "flash-stack" not in source, (
            "the flash markup is back in a client shell; it belongs in the partial"
        )

    partial = (REPO / "templates/partials/flash_messages.html").read_text(
        encoding="utf-8"
    )
    assert 'class="messages flash-stack"' in partial
    assert "x-transition.opacity.duration.200ms" in partial
    # Ten seconds, not three: two-line messages were gone before they could be
    # read. Hovering holds it, and the button dismisses it outright.
    assert "this.visible = false }, 10000)" in partial
    assert '@mouseenter="hold()"' in partial
    assert 'class="message-dismiss"' in partial


def test_jober_shell_separates_adjacent_operational_sections():
    """Feature-contributed panels must not touch a preceding page grid."""
    source = (REPO / "static/src/css/app.css").read_text(encoding="utf-8")
    assert ".app-shell > :is(section, aside, article):not(.page-head)" in source
    assert "+ :is(section, aside, article)" in source
    assert "margin-top: var(--space-4);" in source


def test_trial_outcome_actions_are_neutral_until_chosen():
    source = (REPO / "templates/pages/person_detail.html").read_text(encoding="utf-8")
    assert 'name="scheduled_for" required' in source
    assert (
        'name="outcome" value="pass">\n          <button class="button button-secondary"'
        in source
    )
    assert "Trial destination" in source
    assert "Arrival time" in source


def test_readiness_form_marks_incomplete_or_invalid_fields_for_attention():
    source = (REPO / "templates/pages/person_detail.html").read_text(encoding="utf-8")
    assert "readiness-attention" in source
    assert "readiness-field-error" in source
    assert "x-show=\"accommodation === 'not_applicable'\"" in source
    assert "x-show=\"transport === 'not_applicable'\"" in source


def test_healthz(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.content == b"ok"


def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboard"))
    assert response.status_code == 302
    assert reverse("login") in response.headers["Location"]


@pytest.mark.django_db
def test_dashboard_shell_for_authenticated_user(client, django_user_model):
    user = django_user_model.objects.create_user(
        email="manazer@demo.jober.test", password="x", role="manager"
    )
    client.force_login(user)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    body = response.content.decode("utf-8")
    assert "Reporty" in body
    assert body.count('id="confirm-dialog"') == 1
    assert 'aria-labelledby="confirm-dialog-title"' in body
    # The real-world band (ADR 0034) is described first: when it is shown it is
    # the strongest sentence in the dialog, so it must be announced too.
    assert (
        'aria-describedby="confirm-dialog-physical confirm-dialog-message'
        ' confirm-dialog-prompt"' in body
    )
    assert "data-confirm-cancel" in body
    assert "data-confirm-agree" in body
    assert "Confirmation dialog for destructive actions" not in body
