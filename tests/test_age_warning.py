from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.urls import reverse

from core.people.services import age_warning

pytestmark = pytest.mark.django_db


def test_age_warning_boundaries():
    eighteenth = date(2026, 8, 20)
    birth_date = eighteenth.replace(year=2008)
    assert age_warning(birth_date, on_date=eighteenth - timedelta(days=31))["level"] == "critical"
    assert age_warning(birth_date, on_date=eighteenth - timedelta(days=30))["level"] == "advisory"
    assert age_warning(birth_date, on_date=eighteenth - timedelta(days=1))["level"] == "advisory"
    assert age_warning(birth_date, on_date=eighteenth) is None


def test_age_warning_fragment_requires_login_and_renders(client, django_user_model):
    url = reverse("person_age_warning")
    assert client.get(url, {"date_of_birth": "2010-01-01"}).status_code == 302
    user = django_user_model.objects.create_user(
        email="recruiter@demo.jober.test", password="x", role="recruiter"
    )
    client.force_login(user)
    response = client.get(url, {"date_of_birth": "2010-01-01"})
    assert response.status_code == 200
    assert "age-warning-critical" in response.content.decode()
