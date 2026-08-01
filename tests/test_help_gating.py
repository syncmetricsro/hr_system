from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils import translation

import core.ui.registry as registry
from core.ui.help import (
    article_context,
    article_is_available,
    available_groups,
    raw_article,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def flags(monkeypatch):
    real = registry.flag_enabled

    def _set(**values):
        monkeypatch.setattr(
            registry,
            "flag_enabled",
            lambda name: values.get(name, real(name)),
        )

    return _set


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(
        email="feature-help@demo.invalid", password="x", role="manager"
    )


def _slugs():
    return {a["slug"] for g in available_groups() for a in g["articles"]}


def test_article_without_flags_is_always_available(flags):
    flags(recruitment_trials=False, checklists=False)
    assert article_is_available(raw_article("readiness"))


def test_flagged_article_is_hidden_and_direct_url_is_404(client, reader, flags):
    flags(documents=False)
    assert "compliance" not in _slugs()
    client.force_login(reader)
    assert client.get(reverse("help_article", args=["compliance"])).status_code == 404


def test_conditional_readiness_step_follows_checklist_flag(flags):
    flags(checklists=False)
    without = article_context(raw_article("readiness"))["steps"]
    flags(checklists=True)
    with_checklist = article_context(raw_article("readiness"))["steps"]
    assert len(with_checklist) == len(without) + 1
    with translation.override("en"):
        assert "critical activation item" in str(with_checklist[-1])


def test_equipment_stock_guidance_follows_generic_setting(settings):
    settings.EQUIPMENT_STOCK_LEDGER_ENABLED = False
    without = article_context(raw_article("equipment"))["steps"]
    settings.EQUIPMENT_STOCK_LEDGER_ENABLED = True
    with_stock = article_context(raw_article("equipment"))["steps"]
    assert len(with_stock) == len(without) + 1
    with translation.override("en"):
        assert any("goods receipts" in str(step) for step in with_stock)


def test_equipment_return_guidance_follows_feature_flag(flags):
    flags(equipment_returns=False)
    without = article_context(raw_article("equipment"))["steps"]
    flags(equipment_returns=True)
    with_returns = article_context(raw_article("equipment"))["steps"]
    assert len(with_returns) == len(without) + 1
    with translation.override("en"):
        assert any("Return" in str(step) for step in with_returns)


def test_invalid_asset_namespace_fails_closed(settings):
    settings.HELP_ASSET_NAMESPACE = "../jober"
    with pytest.raises(ImproperlyConfigured, match="HELP_ASSET_NAMESPACE"):
        article_context(raw_article("people"))
