from clients.jober.settings import *  # noqa: F403

DEBUG = False

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
# Secure by default; overridable only so the HTTP-only internal smoke network
# can exercise authenticated flows. Production deployments must leave these on.
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", True)  # noqa: F405
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", True)  # noqa: F405
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Serve collected static files under gunicorn (no separate static server).
# Inserted right after SecurityMiddleware, as WhiteNoise requires. This lives in
# production only: local `runserver` serves static itself and tests do not need it.
MIDDLEWARE = [  # noqa: F405
    MIDDLEWARE[0],  # noqa: F405
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],  # noqa: F405
]

# WhiteNoise compresses and fingerprints static files at collectstatic time and
# serves them with long-lived cache headers and correct content types.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
