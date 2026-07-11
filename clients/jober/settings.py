"""Jober client settings layer (Stage B3, ADR 0021).

Extends the platform base with Jober's policy module, feature flags (all on),
languages, and branding. ``config.settings.local`` / ``.production`` import
from here, so existing ``DJANGO_SETTINGS_MODULE`` values keep working.
"""

from config.settings.base import *  # noqa: F403

CLIENT_POLICIES = "clients.jober.policies"

# Jober mounts every feature (FEATURE_FLAGS defaults in base are already all-on;
# restated here so the client file is the single obvious place to flip one).
FEATURE_FLAGS = {
    "accommodation": True,
    "equipment": True,
    "transport": True,
    "recruitment_trials": True,
    "intake": True,
    "worker_messaging": True,
    "documents": True,
    "feedback": True,
    "duplicate_blacklist": True,
    "profitability": True,
    "checklists": False,   # CorvinumEU feature (ADR 0022) — not in the Jober product
    "advances": False,     # CorvinumEU feature (ADR 0022) — not in the Jober product
    "payslips": False,     # CorvinumEU feature (ADR 0023) — not in the Jober product
}

BRAND_NAME = "Jober"
BRAND_MARK = "JB"
