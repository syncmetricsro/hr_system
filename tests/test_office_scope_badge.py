from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import translation

from core.offices.context_processors import office_scope
from core.offices.models import Office

pytestmark = pytest.mark.django_db


class _Req:
    """Minimal stand-in - the processor only reads request.user."""

    def __init__(self, user):
        self.user = user


def test_badge_is_absent_when_no_offices_exist(django_user_model):
    """CorvinumEU: no office concept, so the shell shows no office marker at
    all rather than an empty or misleading one."""
    manager = django_user_model.objects.create_user(
        email="m@demo.corvinum.test", password="x", role="manager"
    )
    assert Office.objects.count() == 0
    ctx = office_scope(_Req(manager))
    assert ctx["OFFICE_SCOPE_LABEL"] == ""
    assert ctx["OFFICE_SCOPE_UNRESTRICTED"] is False


def test_badge_names_the_single_office_a_manager_is_scoped_to(django_user_model):
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    Office.objects.create(name="Győr", code="GYR", country="HU")
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    ctx = office_scope(_Req(manager))
    assert ctx["OFFICE_SCOPE_LABEL"] == "Velký Meder"
    assert ctx["OFFICE_SCOPE_UNRESTRICTED"] is False


def test_badge_summarises_multi_office_membership(django_user_model):
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    gyor = Office.objects.create(name="Győr", code="GYR", country="HU")
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder, gyor])
    ctx = office_scope(_Req(manager))
    # Alphabetical, so the label is stable rather than depending on insertion.
    assert ctx["OFFICE_SCOPE_LABEL"] == "Győr +1"


def test_observer_badge_says_all_offices(django_user_model):
    Office.objects.create(name="Velký Meder", code="VM", country="SK")
    observer = django_user_model.objects.create_user(
        email="o@demo.jober.test", password="x", role="observer"
    )
    with translation.override("en"):
        ctx = office_scope(_Req(observer))
        assert ctx["OFFICE_SCOPE_LABEL"] == "All offices"
    assert ctx["OFFICE_SCOPE_UNRESTRICTED"] is True


def test_user_with_no_office_membership_is_told_so(django_user_model):
    """Offices exist but this user belongs to none: they genuinely see
    nothing, and the badge should say why instead of leaving a bare screen."""
    Office.objects.create(name="Velký Meder", code="VM", country="SK")
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    with translation.override("en"):
        ctx = office_scope(_Req(manager))
        assert ctx["OFFICE_SCOPE_LABEL"] == "No office"


def test_anonymous_request_renders_no_badge(client):
    Office.objects.create(name="Velký Meder", code="VM", country="SK")

    class _Anon:
        is_authenticated = False

    ctx = office_scope(_Req(_Anon()))
    assert ctx["OFFICE_SCOPE_LABEL"] == ""


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "All offices"),
        ("sk", "Všetky pobočky"),
        ("hu", "Minden iroda"),
        ("uk", "Усі офіси"),
    ],
)
def test_badge_label_is_translated_in_all_ui_languages(
    django_user_model, language, expected
):
    Office.objects.create(name="Velký Meder", code="VM", country="SK")
    observer = django_user_model.objects.create_user(
        email="o@demo.jober.test", password="x", role="observer"
    )
    with translation.override(language):
        assert office_scope(_Req(observer))["OFFICE_SCOPE_LABEL"] == expected


@pytest.mark.jober_only
def test_badge_is_rendered_in_the_shell(client, django_user_model):
    """End-to-end through a real page render, not just the processor."""
    velky_meder = Office.objects.create(name="Velký Meder", code="VM", country="SK")
    manager = django_user_model.objects.create_user(
        email="m@demo.jober.test", password="x", role="manager"
    )
    manager.offices.set([velky_meder])
    client.force_login(manager)
    body = client.get(reverse("reports")).content.decode()
    assert 'class="account-office' in body
    assert "Velký Meder" in body


@pytest.mark.jober_only
def test_observer_shell_badge_uses_the_unrestricted_variant(client, django_user_model):
    Office.objects.create(name="Velký Meder", code="VM", country="SK")
    observer = django_user_model.objects.create_user(
        email="o@demo.jober.test", password="x", role="observer"
    )
    client.force_login(observer)
    with translation.override("en"):
        body = client.get("/en/reports/").content.decode()
    assert "account-office-all" in body
    assert "All offices" in body
