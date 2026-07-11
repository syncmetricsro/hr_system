from __future__ import annotations

import pytest
from django.conf import settings
from django.utils import translation


@pytest.fixture(autouse=True)
def _default_locale():
    """Pin every test to the settings default locale.

    Django's active language is thread-local and survives across tests, so a
    test that activates another language leaks into later ones — which tests
    fail then depends on execution order (bit us in the corvinum lane where
    deselection reshuffles neighbors). Tests that need another language keep
    using ``translation.override(...)`` locally.
    """
    translation.activate(settings.LANGUAGE_CODE)
    yield
    translation.deactivate()
