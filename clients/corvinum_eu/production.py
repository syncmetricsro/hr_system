"""CorvinumEU production/demo settings: the same gunicorn+whitenoise
hardening layer Jober's ``config.settings.production`` applies, over the
CorvinumEU client settings. Used by ``scripts/corvinum_app.sh`` (local demo
over plain HTTP with the secure flags relaxed via env) and later by the real
deployment (flags left at their secure defaults)."""

import os

from clients.corvinum_eu.settings import *  # noqa: F403

DEBUG = False

# Same Dokku persistent-storage mount pattern as config/settings/production.py.
if os.environ.get("MEDIA_ROOT"):
    MEDIA_ROOT = os.environ["MEDIA_ROOT"]  # noqa: F405

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", True)  # noqa: F405
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", True)  # noqa: F405
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

MIDDLEWARE = [  # noqa: F405
    MIDDLEWARE[0],  # noqa: F405
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],  # noqa: F405
]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
