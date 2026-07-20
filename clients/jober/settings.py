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
    "transport": False,
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
    "wage_ledger": False,  # CorvinumEU gross-wage source ledger
}

EQUIPMENT_STOCK_LEDGER_ENABLED = True

BRAND_NAME = "Jober"
BRAND_MARK = "JB"
BRAND_LOGO = "jober/brand/jober-logo.svg"
CLIENT_DEFAULT_THEME = "light"
CLIENT_THEME_STORAGE_KEY = "jober-theme"

# Distinct cookie names per client: both demo apps live on one host
# (localhost:8000/:8001) and browsers scope cookies by host, ignoring ports —
# default names made each login evict the other client's session.
SESSION_COOKIE_NAME = "jober_sessionid"
CSRF_COOKIE_NAME = "jober_csrftoken"
LANGUAGE_COOKIE_NAME = "jober_language"
