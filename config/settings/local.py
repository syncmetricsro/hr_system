from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = [*ALLOWED_HOSTS, "testserver"]  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
