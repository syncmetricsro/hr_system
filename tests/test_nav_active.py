from __future__ import annotations

import pytest
from django.utils import translation

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _contain_language():
    """/en/ requests activate 'en' thread-locally; restore so later tests that
    assert Slovak content (test_shell) are unaffected (see CLAUDE.md gotcha)."""
    with translation.override("sk"):
        yield


@pytest.fixture
def manager_client(client, django_user_model):
    user = django_user_model.objects.create_user(
        email="nav@demo.jober.test", password="x", role="manager"
    )
    client.force_login(user)
    return client


def _active_hrefs(html: str) -> list[str]:
    """hrefs of nav links carrying is-active."""
    import re
    return re.findall(r'class="folder-tab is-active"\s+href="([^"]+)"', html)


def test_dashboard_tab_active_on_dashboard(manager_client):
    html = manager_client.get("/en/").content.decode()
    assert _active_hrefs(html) == ["/en/"]


def test_people_tab_active_on_people_pages(manager_client):
    html = manager_client.get("/en/people/").content.decode()
    assert _active_hrefs(html) == ["/en/people/"]
    # Overview must NOT stay highlighted (the old hardcoded bug).
    assert 'is-active" href="/en/"' not in html


def test_finance_tab_active_on_month_detail(manager_client):
    from apps.finance.models import FinancialMonth
    from apps.projects.models import Project

    project = Project.objects.create(name="DHL", code="DHLBA")
    month = FinancialMonth.objects.create(project=project, year=2026, month=5)
    html = manager_client.get(f"/en/finance/month/{month.pk}/").content.decode()
    assert _active_hrefs(html) == ["/en/finance/"]


def test_exactly_one_active_tab(manager_client):
    for path in ["/en/", "/en/people/", "/en/reports/", "/en/blacklist/", "/en/compliance/"]:
        html = manager_client.get(path).content.decode()
        assert len(_active_hrefs(html)) == 1, path
