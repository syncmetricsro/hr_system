"""Help articles must match the client's feature set (J9, plan item 10).

Every article shipped to every client. A CorvinumEU user was offered - and
could open - articles explaining Feedback, Finance reports and accommodation,
none of which that client's app has. Documentation for a feature you cannot
reach is worse than none: it reads as something broken or missing rather than
absent by design.

The gate is per feature flag, not per role. Roles still see every article they
are entitled to; the design doc is explicit that documentation is not
role-gated, and that stays true.
"""

from __future__ import annotations

import pytest
from django.urls import reverse

import core.ui.registry as registry
from core.ui.help import HELP_GROUPS, article_is_available, available_groups

pytestmark = pytest.mark.django_db


@pytest.fixture
def flags_off(monkeypatch):
    """Turn named flags off for the duration of a test.

    Deliberately patches the flag *lookup* rather than `settings.FEATURE_FLAGS`:
    changing that setting rebuilds the URLconf, because `config/urls.py`
    registers routes per flag at import time. A test that flips a flag to check
    a Help article would silently unregister unrelated URLs and fail somewhere
    else entirely - which is exactly what happened writing this file.
    """
    real = registry.flag_enabled

    def _off(*names):
        monkeypatch.setattr(
            registry,
            "flag_enabled",
            lambda flag: False if flag in names else real(flag),
        )

    return _off


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(
        email="ktokolvek@demo.jober.test", password="x", role="manager"
    )


def _slugs(groups):
    return {a["slug"] for g in groups for a in g["articles"]}


# --- the gate itself ---------------------------------------------------------


def test_an_article_with_no_flags_is_always_available():
    """Getting started, People, Projects and Audit describe the shared core."""
    assert article_is_available({"slug": "getting-started"}) is True


def test_an_article_is_available_when_any_of_its_flags_is_on(flags_off):
    """Logistics covers accommodation, equipment and transport; CorvinumEU has
    only equipment, and the article is still worth reading there."""
    flags_off("accommodation", "transport")
    article = next(
        a for g in HELP_GROUPS for a in g["articles"] if a["slug"] == "logistics"
    )
    assert article_is_available(article) is True


def test_an_article_is_hidden_when_every_flag_is_off(flags_off):
    flags_off("accommodation", "transport", "equipment")
    article = next(
        a for g in HELP_GROUPS for a in g["articles"] if a["slug"] == "logistics"
    )
    assert article_is_available(article) is False


def test_a_group_left_with_no_articles_disappears(flags_off):
    flags_off("feedback")
    assert "feedback" not in _slugs(available_groups())
    assert all(g["articles"] for g in available_groups())


# --- the index and the article itself ---------------------------------------


def test_the_index_lists_only_available_articles(client, reader, flags_off):
    flags_off("profitability")
    client.force_login(reader)
    body = client.get(reverse("help_index")).content.decode()
    assert reverse("help_article", args=["finance"]) not in body
    assert reverse("help_article", args=["people"]) in body


def test_a_hidden_article_is_not_reachable_by_url(client, reader, flags_off):
    """Otherwise the gate is decoration. The Help index is the only signpost,
    but a URL survives in a bookmark, a chat message or a stale link."""
    flags_off("feedback")
    client.force_login(reader)
    assert client.get(reverse("help_article", args=["feedback"])).status_code == 404


@pytest.mark.jober_only
def test_an_available_article_still_opens(client, reader):
    """Guard the opposite failure: gating everything off would satisfy the
    test above while removing the Help area.

    Jober-only because it names a flagged article deliberately - an
    always-available one would pass even if the gate rejected everything
    flagged, which is the failure being guarded against."""
    client.force_login(reader)
    assert client.get(reverse("help_article", args=["feedback"])).status_code == 200


def test_documentation_is_still_not_role_gated(client, django_user_model):
    """The design doc is explicit that every role gets documentation. The flag
    gate must not quietly become a permission gate."""
    recruiter = django_user_model.objects.create_user(
        email="naborar@demo.jober.test", password="x", role="recruiter"
    )
    client.force_login(recruiter)
    assert client.get(reverse("help_index")).status_code == 200
    assert client.get(reverse("help_article", args=["audit"])).status_code == 200


@pytest.mark.jober_only
def test_jober_still_sees_every_article(client, reader):
    """Jober has all of these features; nothing should have been hidden."""
    client.force_login(reader)
    assert _slugs(available_groups()) == _slugs(HELP_GROUPS)
