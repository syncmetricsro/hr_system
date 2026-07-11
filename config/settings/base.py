from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-only-change-me")
DEBUG = env_bool("DJANGO_DEBUG", False)

if not DEBUG and SECRET_KEY == "insecure-dev-only-change-me":
    raise RuntimeError("DJANGO_SECRET_KEY must be set outside local development.")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

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
    "features.logistics",
    "features.finance",
    "features.intake",
    "features.messaging",
    "features.compliance",
    "features.feedback",
    "features.blacklist",
    "features.checklists",
    "features.advances",
    "features.payslips",
    "core.ui",
    "clients.jober.demo",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.ui.context_processors.brand",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "jober"),
        "USER": os.getenv("DB_USER", "jober"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Source strings are authored in English (the base/fallback language); the active
# default shown to visitors is Slovak. SK/HU/UK ship as translation catalogs.
LANGUAGE_CODE = "sk"
LANGUAGES = [
    ("en", "English"),
    ("sk", "Slovenčina"),
    ("hu", "Magyar"),
    ("uk", "Українська"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Bratislava"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# One artifact serves every client (§12.4), so collectstatic must gather all
# client static dirs regardless of which client settings module built it.
STATICFILES_DIRS = [BASE_DIR / "static"] + sorted((BASE_DIR / "clients").glob("*/static"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# Single switch for the still-open GDPR recruiter/coordinator read-scope
# decision. Defaults to broad internal reads (plan §8.1 / ADR 0008); do not
# hardcode a narrower split until Jober confirms (docs/product/jober-open-decisions.md).
BROAD_INTERNAL_READS = env_bool("JOBER_BROAD_INTERNAL_READS", True)

# Twilio SMS — credentials come from the environment only, never the repo.
# Unset = SMS is "not configured" and sends fail closed (dev/demo default).
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")

# Compliance alerting windows. Medical validity drives the medical expiry alert;
# the alert window is how far ahead a paper counts as "expiring" (≈ the 11/23-month
# pattern = ~1 month before a 12/24-month validity).
MEDICAL_VALIDITY_MONTHS = int(os.getenv("MEDICAL_VALIDITY_MONTHS", "12"))
COMPLIANCE_ALERT_DAYS = int(os.getenv("COMPLIANCE_ALERT_DAYS", "30"))

# Worker feedback is retained briefly only (plan §11.11 ≈ 1 month).
FEEDBACK_RETENTION_DAYS = int(os.getenv("FEEDBACK_RETENTION_DAYS", "31"))

# Blacklist & HMAC matching (plan §11.14). Legal basis: legitimate interest
# (fraud prevention / security vetting / hiring decisions). Real-data execution
# stays gated on the LIA + lawyer sign-off — until then fictional data only.
#   - HMAC keys: comma-separated, newest last; the index is the stored key_version
#     so keys can rotate without re-hashing. Dev falls back to SECRET_KEY.
#   - MATCHING_ENABLED: the §11.14 "approved before production execution" gate.
#   - RETENTION_DAYS: fingerprint/case retention (≈5y placeholder, pending approval).
BLACKLIST_HMAC_KEYS = [
    k for k in os.getenv("BLACKLIST_HMAC_KEYS", SECRET_KEY).split(",") if k
]
BLACKLIST_MATCHING_ENABLED = env_bool("BLACKLIST_MATCHING_ENABLED", True)
BLACKLIST_RETENTION_DAYS = int(os.getenv("BLACKLIST_RETENTION_DAYS", "1825"))

# ---------------------------------------------------------------------------
# Platform (Stage B, ADR 0021). Feature flags gate which optional modules a
# client mounts (URLs/nav/panels/registrations consult these); CLIENT_POLICIES
# names the module supplying client-specific policy data (roles matrix,
# lifecycle values, sensitive-visibility). Jober = everything on. Sub-features
# of physically-unsplit apps (accommodation/equipment/transport inside
# logistics; trials inside projects) get their own keys per the extraction
# plan's recorded deviation.
FEATURE_FLAGS = {
    "accommodation": True,
    "equipment": True,
    "transport": True,
    "recruitment_trials": True,
    "intake": True,
    "worker_messaging": True,
    "documents": True,        # compliance certificates
    "feedback": True,
    "duplicate_blacklist": True,
    "profitability": True,    # finance
    "checklists": False,      # CorvinumEU feature (ADR 0022); a client opts in
    "advances": False,        # CorvinumEU feature (ADR 0022); a client opts in
    "payslips": False,        # CorvinumEU feature (ADR 0023); a client opts in
}
CLIENT_POLICIES = os.getenv("CLIENT_POLICIES", "core.accounts.default_policies")

# Email delivery (ADR 0023 payslips). Default is Django's SMTP backend —
# real deployments configure the SMTP host via env/Doppler; the local demo
# scripts point this at the console backend instead.
EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("DJANGO_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("DJANGO_EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_DEFAULT_FROM_EMAIL", "noreply@localhost")

# Roles that must enroll a TOTP device (Stage B4b). Empty for Jober => zero
# behavior change; CorvinumEU will require it for HR/admin/manager (§5.12).
TWO_FACTOR_REQUIRED_ROLES: list[str] = []

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
