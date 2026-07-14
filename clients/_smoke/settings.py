"""Synthetic core-only client (Stage B3/B5 validation, ADR 0021).

Boots the platform with NO feature apps and NO client policies — proving the
core is self-sufficient: neutral deny-by-default policies, permissive workflow,
no feature URLs mounted. Used by `manage.py check` in the smoke test; not a
real deployment target.
"""

from config.settings.base import *  # noqa: F403

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.accounts",
    "core.audit",
    "core.people",
    "core.projects",
    "core.retention",
    "core.notifications",
    "core.ui",
]

CLIENT_POLICIES = "core.accounts.default_policies"
FEATURE_FLAGS = {key: False for key in FEATURE_FLAGS}  # noqa: F405

BRAND_NAME = "Platform"
BRAND_MARK = "P"
