"""CorvinumEU PeopleOps client settings layer (Stage C0, ADR 0022).

The second thin client on the Stage B core: an explicit INSTALLED_APPS set
(feature migrations run only where the feature is installed — design doc
§12.4), CorvinumEU's flag set, SK/HU languages, branding, and 2FA required
for managers (§5.12). Defaults for unconfirmed client decisions are tracked
in docs/product/corvinum-open-questions.md.
"""

from config.settings.base import *  # noqa: F403

CLIENT_POLICIES = "clients.corvinum_eu.policies"

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
    "features.logistics",     # equipment only — see FEATURE_FLAGS
    "features.intake",
    "features.compliance",
    "features.blacklist",
    "core.ui",
]

FEATURE_FLAGS = {
    "accommodation": False,       # rejected in interview (§15.4)
    "equipment": True,            # issued items + cost recovery (§5.8)
    "transport": False,           # rejected in interview (§15.8)
    "recruitment_trials": False,  # test/trial handling unconfirmed for MVP (§13.1)
    "intake": True,
    "worker_messaging": False,    # phone + Messenger, no SMS module (§15.9)
    "documents": True,            # compliance certificates + expiry (§5.4)
    "feedback": False,            # worker portal rejected (§16)
    "duplicate_blacklist": True,  # §5.6
    "profitability": False,       # no P&L dashboards (§15.6)
    "checklists": False,          # flips on when features/checklists lands (C1)
    "advances": False,            # flips on when features/advances lands (C2)
}

# Bilingual SK/HU (confirmed); SK default pending confirmation (C-Q8).
LANGUAGES = [
    ("sk", "Slovenčina"),
    ("hu", "Magyar"),
]

# Security baseline §5.12: admins/managers must enroll TOTP (core Stage B4b).
TWO_FACTOR_REQUIRED_ROLES = ["manager"]

BRAND_NAME = "CorvinumEU PeopleOps"
BRAND_MARK = "CE"
