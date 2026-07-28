from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.ui.help import ARTICLE_TEMPLATES, available_groups

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_user(django_user_model):
    def _make(role):
        return django_user_model.objects.create_user(
            email=f"{role}@demo.jober.test", password="x", role=role
        )

    return _make


def test_help_index_requires_login(client):
    resp = client.get(reverse("help_index"))
    assert resp.status_code == 302
    assert reverse("login") in resp.headers["Location"]


@pytest.mark.parametrize("role", ["recruiter", "coordinator", "manager", "observer"])
def test_help_index_visible_to_every_role(client, make_user, role):
    """No RBAC gate - every role needs documentation (help-area-design.md)."""
    client.force_login(make_user(role))
    resp = client.get(reverse("help_index"))
    assert resp.status_code == 200


def test_help_index_lists_every_group_and_article(client, make_user):
    client.force_login(make_user("recruiter"))
    body = client.get(reverse("help_index")).content.decode()
    # Articles are gated by feature flag, so the index lists what *this* client
    # actually has - CorvinumEU has no Feedback or Finance reporting.
    for group in available_groups():
        for article in group["articles"]:
            assert reverse("help_article", args=[article["slug"]]) in body


@pytest.mark.parametrize("slug", list(ARTICLE_TEMPLATES))
def test_each_help_article_renders(client, make_user, slug):
    """Every article this client offers must render.

    Parametrized over all slugs rather than the available ones so a template
    that breaks stays visible in the report; an article the client does not
    have is asserted to 404 instead, which is the gate working.
    """
    client.force_login(make_user("observer"))
    resp = client.get(reverse("help_article", args=[slug]))
    available = {a["slug"] for g in available_groups() for a in g["articles"]}
    assert resp.status_code == (200 if slug in available else 404)


def test_unknown_help_slug_is_404(client, make_user):
    client.force_login(make_user("manager"))
    resp = client.get(reverse("help_article", args=["not-a-real-article"]))
    assert resp.status_code == 404


def test_help_article_requires_login(client):
    resp = client.get(reverse("help_article", args=["getting-started"]))
    assert resp.status_code == 302
    assert reverse("login") in resp.headers["Location"]


def test_help_nav_tab_appears_for_every_role(client, make_user):
    """Unconditional tab - not gated by any Action or feature flag."""
    client.force_login(make_user("observer"))
    body = client.get(reverse("people_list")).content.decode()
    assert reverse("help_index") in body


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("sk", "Začíname"),
        ("hu", "Első lépések"),
    ],
)
def test_help_article_titles_are_translated(client, make_user, language, expected):
    """sk/hu are shared by both clients; uk is Jober-only (CorvinumEU's
    LANGUAGES doesn't include it - a pre-existing client policy, not
    something this feature changes) and is covered separately below."""
    client.force_login(make_user("manager"))
    resp = client.get(f"/{language}/help/getting-started/")
    assert resp.status_code == 200
    assert expected in resp.content.decode()


@pytest.mark.jober_only
def test_help_article_title_translated_uk(client, make_user):
    client.force_login(make_user("manager"))
    resp = client.get("/uk/help/getting-started/")
    assert resp.status_code == 200
    assert "Початок роботи" in resp.content.decode()


def test_help_index_translated_group_labels(client, make_user):
    client.force_login(make_user("manager"))
    resp = client.get("/hu/help/")
    body = resp.content.decode()
    assert "Súgó" in body
    assert "Megfelelőség" in body


@pytest.mark.jober_only
def test_help_index_translated_group_labels_uk(client, make_user):
    client.force_login(make_user("manager"))
    resp = client.get("/uk/help/")
    body = resp.content.decode()
    assert "Довідка" in body
    assert "Аудит" in body


def test_getting_started_article_content_in_english():
    with translation.override("en"):
        from django.utils.translation import gettext

        assert gettext("Getting started") == "Getting started"
        assert gettext("Roles") == "Roles"
