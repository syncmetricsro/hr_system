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
    assert "Prevádzkový prehľad" in body
    assert body.count('id="confirm-dialog"') == 1
    assert 'aria-labelledby="confirm-dialog-title"' in body
    assert 'aria-describedby="confirm-dialog-message confirm-dialog-prompt"' in body
    assert "data-confirm-cancel" in body
    assert "data-confirm-agree" in body
    assert "Confirmation dialog for destructive actions" not in body
