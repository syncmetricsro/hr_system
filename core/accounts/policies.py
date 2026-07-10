"""Client-policy loader (Stage B3, ADR 0021).

The core never branches on client identity. Where clients legitimately differ —
role grants, lifecycle transition values, sensitive-field visibility — the core
resolves a policy module named by ``settings.CLIENT_POLICIES`` and calls it.
``core.accounts.default_policies`` ships neutral, deny-by-default values so the
core boots without any client.
"""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module

from django.conf import settings


@lru_cache(maxsize=None)
def _load(path: str):
    return import_module(path)


def get_policies():
    return _load(
        getattr(settings, "CLIENT_POLICIES", "core.accounts.default_policies")
    )
