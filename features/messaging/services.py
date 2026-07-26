from __future__ import annotations

import base64
import hashlib
import hmac
import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

from core.audit.services import record_event
from features.messaging.models import OutboundMessage

TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"


class SmsNotConfigured(Exception):
    """Twilio credentials are not set in the environment."""


class SmsSendError(Exception):
    """The provider rejected or failed the send."""


class SmsRecipientNotAllowed(Exception):
    """A non-production allowlist stopped the send before the provider."""


def sms_configured() -> bool:
    """Whether a send could actually reach Twilio.

    Exposed so the UI can *say* messaging is unavailable instead of offering a
    Send button that records a failure. An unconfigured environment is a
    normal state (local, CI, a client with SMS off), not a fault.
    """
    return all(
        (
            getattr(settings, "TWILIO_ACCOUNT_SID", ""),
            getattr(settings, "TWILIO_AUTH_TOKEN", ""),
            getattr(settings, "TWILIO_FROM_NUMBER", ""),
        )
    )


def _comparable(number: str) -> str:
    """Reduce a phone number to digits (and a leading +) so an allowlist entry
    matches however the number was typed - '+421 900 000 000', '+421900000000'
    and '+421-900-000-000' are the same handset."""
    return "".join(ch for ch in (number or "") if ch.isdigit() or ch == "+")


def _assert_recipient_allowed(to_number: str) -> None:
    allowed = getattr(settings, "SMS_ALLOWED_RECIPIENTS", []) or []
    if not allowed:  # Empty = unrestricted; production's setting.
        return
    if _comparable(to_number) not in {_comparable(n) for n in allowed}:
        raise SmsRecipientNotAllowed(
            "This environment may only message its configured test number."
        )


def _twilio_send(to_number: str, body: str) -> str:
    """POST to Twilio's REST API via the standard library (no SDK). Returns the
    message SID. Credentials come from the environment, never the repo."""
    sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_number = getattr(settings, "TWILIO_FROM_NUMBER", "")
    if not (sid and token and from_number):
        raise SmsNotConfigured("Twilio credentials are not configured.")

    url = TWILIO_API.format(sid=sid)
    data = urllib.parse.urlencode(
        {"From": from_number, "To": to_number, "Body": body}
    ).encode()
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 (pinned https URL)
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise SmsSendError(f"Twilio HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise SmsSendError(str(exc.reason)) from exc
    return payload.get("sid", "")


def send_sms(to_number: str, body: str, *, actor=None, person=None) -> OutboundMessage:
    message = OutboundMessage.objects.create(
        person=person,
        to_number=to_number,
        body=body,
        sent_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    try:
        # Allowlist first: a blocked send must never reach the provider, and
        # must not be recorded as a provider failure.
        _assert_recipient_allowed(to_number)
        sid = _twilio_send(to_number, body)
        message.status = OutboundMessage.Status.SENT
        message.provider_sid = sid
    except SmsRecipientNotAllowed as exc:
        message.status = OutboundMessage.Status.BLOCKED
        message.error = str(exc)[:300]
    except (SmsNotConfigured, SmsSendError) as exc:
        message.status = OutboundMessage.Status.FAILED
        message.error = str(exc)[:300]
    message.save(update_fields=["status", "provider_sid", "error"])
    record_event(actor, "sms.sent", target=message, status=message.status, to=to_number)
    return message


def verify_twilio_signature(url: str, params: dict, signature: str) -> bool:
    """Validate the X-Twilio-Signature header (fail closed). Algorithm: base64
    HMAC-SHA1 of (url + sorted concatenated POST params) keyed by the auth token."""
    token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    if not token or not signature:
        return False
    base = url + "".join(f"{key}{params[key]}" for key in sorted(params))
    digest = hmac.new(token.encode(), base.encode("utf-8"), hashlib.sha1).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)
