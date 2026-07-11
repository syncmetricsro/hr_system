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
    "features.checklists",
    "features.advances",
    "features.payslips",
    "core.ui",
    "clients.corvinum_eu.demo",
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
    "checklists": True,           # approval checklists (§5.5, Stage C1)
    "advances": True,             # advance & deduction ledger (§5.10, Stage C2)
    "payslips": True,             # encrypted payslip email (ADR 0023, Stage C5)
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

# corvinum.eu design language layered over the shared shell (§7.0; C-Q8
# dark-default pending confirmation). The client static dir is collected by
# base's STATICFILES_DIRS glob — one artifact carries every client's theme.
CLIENT_THEME_CSS = "corvinum/theme.css"

# Client template layer (Stage C8): the corvinum shell overrides
# layouts/base.html (left slide-out sidebar per the peopleops prototype);
# every other template falls through to the shared tree.
TEMPLATES[0]["DIRS"] = [  # noqa: F405
    BASE_DIR / "clients" / "corvinum_eu" / "templates",  # noqa: F405
    BASE_DIR / "templates",  # noqa: F405
]

# Distinct cookie names per client (see clients/jober/settings.py).
SESSION_COOKIE_NAME = "corvinum_sessionid"
CSRF_COOKIE_NAME = "corvinum_csrftoken"
