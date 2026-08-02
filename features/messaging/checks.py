"""Deploy-time safety check for offer emails (ADR 0029).

The allowlist is what stops a staging box emailing a real inbox, and an empty
allowlist is *correct* in production — so it cannot simply be made mandatory.
What can be caught is the dangerous combination: outreach enabled, a real mail
server configured, DEBUG off, and nothing restricting recipients. This is the
practical execution gate, in place of yet another boolean switch nobody
remembers to flip.
"""

from __future__ import annotations

from django.conf import settings
from django.core.checks import Warning as CheckWarning
from django.core.checks import register


@register()
def offer_email_allowlist_check(app_configs, **kwargs):
    if not getattr(settings, "FEATURE_FLAGS", {}).get("offer_emails", False):
        return []
    if "smtp" not in getattr(settings, "EMAIL_BACKEND", ""):
        return []
    if getattr(settings, "EMAIL_ALLOWED_RECIPIENTS", []):
        return []
    return [
        CheckWarning(
            "Offer emails are enabled with a real SMTP backend and no recipient "
            "allowlist.",
            hint=(
                "Set EMAIL_ALLOWED_RECIPIENTS to the demo inbox on every "
                "non-production app. Fictional worker records can hold real "
                "addresses, so 'the data is fake' is not a control. Leave it "
                "empty only in production."
            ),
            id="messaging.W001",
        )
    ]
