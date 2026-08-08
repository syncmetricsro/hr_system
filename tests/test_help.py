from __future__ import annotations

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import translation

from core.ui.help import ARTICLE_TEMPLATES, available_articles, available_groups
from core.ui.icons import ICONS

pytestmark = pytest.mark.django_db

COMMON = {
    "getting-started",
    "people",
    "projects",
    "readiness",
    "compliance",
    "equipment",
    "reports",
    "blacklist",
    "audit",
}
EXPECTED = {
    "jober": COMMON | {"accommodation", "finance", "feedback"},
    "corvinum": COMMON | {"ledger", "payslips", "gross-wages"},
}


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(
        email="help.reader@demo.invalid", password="x", role="observer"
    )


def _slugs() -> list[str]:
    return [article["slug"] for article in available_articles()]


def test_help_requires_login(client):
    assert client.get(reverse("help_index")).status_code == 302
    assert (
        client.get(reverse("help_article", args=["getting-started"])).status_code == 302
    )


@pytest.mark.parametrize("role", ["recruiter", "coordinator", "manager", "observer"])
def test_help_index_is_readable_by_every_authenticated_role(
    client, django_user_model, role
):
    user = django_user_model.objects.create_user(
        email=f"help-{role}@demo.invalid", password="x", role=role
    )
    client.force_login(user)
    assert client.get(reverse("help_index")).status_code == 200


def test_each_client_has_exactly_twelve_supported_topics():
    assert set(_slugs()) == EXPECTED[settings.HELP_ASSET_NAMESPACE]
    assert len(_slugs()) == 12
    assert len(_slugs()) == len(set(_slugs()))


def test_index_groups_are_nonempty_and_preserve_the_same_twelve_topics():
    groups = available_groups()
    assert all(group["articles"] for group in groups)
    assert [a["slug"] for g in groups for a in g["articles"]] == _slugs()


def test_every_card_has_complete_semantic_metadata():
    for article in available_articles():
        assert article["icon"] in ICONS
        assert str(article["summary"]).strip()
        assert article["thumbnail"].endswith(f"/{article['slug']}-thumb.webp")
        assert article["screenshots"]
        assert all(str(screen["alt"]).strip() for screen in article["screenshots"])
        assert all(screen["callouts"] for screen in article["screenshots"])


def test_index_renders_every_available_link_and_no_other_article(client, reader):
    client.force_login(reader)
    body = client.get(reverse("help_index")).content.decode()
    for slug in ARTICLE_TEMPLATES:
        link = reverse("help_article", args=[slug])
        assert (link in body) is (slug in set(_slugs()))
    assert body.count('class="help-card"') == 12


@pytest.mark.parametrize("slug", list(ARTICLE_TEMPLATES))
def test_each_article_renders_or_returns_404_when_unsupported(client, reader, slug):
    client.force_login(reader)
    response = client.get(reverse("help_article", args=[slug]))
    assert response.status_code == (200 if slug in set(_slugs()) else 404)


def test_article_has_the_shared_instructional_structure(client, reader):
    client.force_login(reader)
    body = client.get(reverse("help_article", args=["people"])).content.decode()
    for anchor in ("purpose", "permissions", "workflow", "boundary", "example"):
        assert f'id="{anchor}"' in body
        assert f'href="#{anchor}"' in body
    assert 'class="help-workflow"' in body
    assert 'class="help-figure-marker"' in body
    assert 'id="related"' in body


def test_related_topics_are_filtered_to_this_client(client, reader):
    client.force_login(reader)
    body = client.get(reverse("help_article", args=["reports"])).content.decode()
    assert reverse("help_article", args=["audit"]) in body
    unavailable = {"jober": "ledger", "corvinum": "finance"}[
        settings.HELP_ASSET_NAMESPACE
    ]
    assert reverse("help_article", args=[unavailable]) not in body


def test_legacy_logistics_url_redirects_to_equipment(client, reader):
    client.force_login(reader)
    response = client.get(reverse("help_article", args=["logistics"]))
    assert response.status_code == 301
    assert response.headers["Location"] == reverse("help_article", args=["equipment"])


def test_unknown_help_slug_is_404(client, reader):
    client.force_login(reader)
    assert (
        client.get(reverse("help_article", args=["not-a-real-article"])).status_code
        == 404
    )


@pytest.mark.parametrize(
    ("language", "expected"),
    [("sk", "Začíname"), ("hu", "Első lépések")],
)
def test_getting_started_title_is_translated(client, reader, language, expected):
    client.force_login(reader)
    response = client.get(f"/{language}/help/getting-started/")
    assert response.status_code == 200
    assert expected in response.content.decode()


@pytest.mark.jober_only
def test_getting_started_title_is_translated_to_ukrainian(client, reader):
    client.force_login(reader)
    response = client.get("/uk/help/getting-started/")
    assert response.status_code == 200
    assert "Початок роботи" in response.content.decode()


def test_every_visible_navigation_workflow_has_help_coverage():
    covered = {route for article in available_articles() for route in article["covers"]}
    expected = {
        "jober": {
            "people_list",
            "project_list",
            "trials_queue",
            "compliance_list",
            "accommodation_list",
            "reports",
            "help_index",
            "staff_activity",
            "audit_log",
            "equipment_reviews",
            "equipment_stock",
            "activation_queue",
            "blacklist_queue",
            "finance_summary",
            "feedback_inbox",
        },
        "corvinum": {
            "people_list",
            "project_list",
            "trials_queue",
            "compliance_list",
            "reports",
            "help_index",
            "staff_activity",
            "audit_log",
            "equipment_catalog",
            "equipment_reviews",
            "activation_queue",
            "blacklist_queue",
            "ledger_overview",
            "payslip_list",
            "wage_list",
            "offer_list",
        },
    }[settings.HELP_ASSET_NAMESPACE]
    assert expected <= covered


def test_base_english_content_remains_available():
    with translation.override("en"):
        assert str(available_articles()[0]["title"]) == "Getting started"


def test_offer_help_step_and_navigation_coverage_follow_the_feature_flag(settings):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "offer_emails": False}
    people = next(a for a in available_articles() if a["slug"] == "people")
    assert "offer_list" not in people["covers"]

    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "offer_emails": True}
    people = next(a for a in available_articles() if a["slug"] == "people")
    assert "offer_list" in people["covers"]
    with translation.override("en"):
        assert any(
            "nobody is selected by default" in str(step) for step in people["steps"]
        )


@pytest.mark.jober_only
def test_finance_help_describes_the_current_write_and_reporting_surfaces(
    client, reader
):
    client.force_login(reader)
    response = client.get("/en/help/finance/")

    assert response.status_code == 200
    body = response.content.decode()
    for expected in (
        "Record a month",
        "Revenue and Cost as positive totals",
        "For bulk entry",
        "View whole year",
        "Year and Months sheets",
        "values, not worksheet formulas",
        "changing a downloaded file cannot change the application",
    ):
        assert expected in body

    finance = next(
        article for article in available_articles() if article["slug"] == "finance"
    )
    assert {
        "finance_summary",
        "finance_workbook",
        "finance_workbook_year",
        "finance_project_year",
    } <= set(finance["covers"])
