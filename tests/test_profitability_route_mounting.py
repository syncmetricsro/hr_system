from __future__ import annotations

import pytest
from django.apps import apps
from django.urls import Resolver404, resolve


def test_annual_profitability_workbook_is_mounted_only_with_the_feature():
    path = "/sk/finance/workbook/2026/"
    if apps.is_installed("features.profitability"):
        assert resolve(path).url_name == "finance_workbook_year"
    else:
        with pytest.raises(Resolver404):
            resolve(path)
