from __future__ import annotations

import pytest
from django.conf import settings
from django.urls import NoReverseMatch, reverse

pytestmark = [pytest.mark.django_db, pytest.mark.jober_only]


def test_jober_transport_is_disabled_and_routes_are_unmounted():
    assert settings.FEATURE_FLAGS["transport"] is False
    with pytest.raises(NoReverseMatch):
        reverse("transport_trends")
