from __future__ import annotations

import pytest

from core.accounts.permissions import user_office_scope
from core.offices.models import Office

pytestmark = pytest.mark.django_db


def test_user_office_scope_is_unrestricted_when_no_offices_exist_at_all(
    django_user_model,
):
    """CorvinumEU's permanent condition: zero Office rows anywhere. Every
    non-Observer role must still be unrestricted (None), not empty - an
    empty queryset would mean "restricted to nothing" everywhere this
    helper's result is used as a `.filter(office__in=scope)` clause."""
    manager = django_user_model.objects.create_user(
        email="mgr@demo.corvinum.test", password="x", role="manager"
    )
    assert Office.objects.count() == 0
    assert user_office_scope(manager) is None


def test_user_office_scope_restricts_when_offices_exist_but_user_has_none(
    django_user_model,
):
    """Once real Office rows exist (Jober), a user genuinely belonging to
    zero of them must still be restricted to nothing - the fail-closed
    case the helper's docstring already promised must keep working."""
    Office.objects.create(name="Velký Meder", code="VM", country="SK")
    manager = django_user_model.objects.create_user(
        email="mgr@demo.jober.test", password="x", role="manager"
    )
    scope = user_office_scope(manager)
    assert scope is not None
    assert list(scope) == []
