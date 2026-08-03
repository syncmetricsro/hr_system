"""Deploy-time safety checks for outbound email (ADR 0023 / ADR 0029).

The recipient allowlist is what stops a staging box emailing a real inbox, and
an empty allowlist is *correct* in production — so it cannot simply be made
mandatory. What can be caught is the dangerous combination: a feature that
emails workers is enabled, a real mail server is configured, DEBUG is off, and
nothing restricts recipients.

This lives in core rather than in a feature because the two senders ship to
different clients: Jober has offer emails, CorvinumEU has payslips. A check
registered inside ``features.messaging`` never runs for CorvinumEU at all.
"""

from __future__ import annotations

from django.conf import settings
from django.core.checks import Warning as CheckWarning
from django.core.checks import register

from core.mail import WORKER_EMAIL_FLAGS, allowed_recipients


@register()
def worker_email_allowlist_check(app_configs, **kwargs):
    flags = getattr(settings, "FEATURE_FLAGS", {})
    enabled = [flag for flag in WORKER_EMAIL_FLAGS if flags.get(flag, False)]
    if not enabled:
        return []
    if "smtp" not in getattr(settings, "EMAIL_BACKEND", ""):
        return []
    if getattr(settings, "DEBUG", False):
        return []
    if allowed_recipients():
        return []
    return [
        CheckWarning(
            "Worker email is enabled (%s) with a real SMTP backend and no "
            "recipient allowlist." % ", ".join(enabled),
            hint=(
                "Set EMAIL_ALLOWED_RECIPIENTS to the controlled demo inbox on "
                "every non-production app. Fictional worker records can hold "
                "real addresses, so 'the data is fake' is not a control. Leave "
                "it empty only in production."
            ),
            id="mail.W001",
        )
    ]
