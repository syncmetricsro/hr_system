from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import json
import string
import urllib.error
import urllib.parse
import urllib.request
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

from core.audit.services import record_event
from core.mail import (
    EmailRecipientNotAllowed,
    assert_recipient_allowed,
    email_configured,
)
from core.people.models import LifecycleStatus
from features.messaging.models import (
    EmailBatch,
    OfferEmailTemplate,
    OutboundEmail,
    OutboundMessage,
)

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


# ---------------------------------------------------------------------------
# Offer emails (ADR 0029)
#
# Same shape as send_sms above - create the record first, then decide, so a
# refused send is still evidence - but a different transport, a different
# record, and one extra class of guard: SMS only ever asks "may this
# environment reach this handset", while an offer email must also ask whether
# this *worker* still wants to hear from us.
# ---------------------------------------------------------------------------


class EmailNotConfigured(Exception):
    """No usable mail backend for this environment."""


class EmailSendError(Exception):
    """The mail server rejected or failed the send."""


class OfferEmailBlocked(Exception):
    """The worker's own state stops this send (opt-out, blacklist, no address)."""


class OfferTemplateMissing(Exception):
    """No active template exists for this kind in any usable language."""


def _offer_language(person) -> str:
    """The language to write to this worker in.

    ``preferred_language`` is a free CharField, so an unusable value falls back
    to the site default rather than failing the send.
    """
    available = {code for code, _label in settings.LANGUAGES}
    preferred = (getattr(person, "preferred_language", "") or "").strip()
    if preferred in available:
        return preferred
    return settings.LANGUAGE_CODE


def _coordinator_name(person) -> str:
    """Display name of a coordinator responsible for this person, if any."""
    from core.accounts.models import User

    coordinator = User.objects.filter(
        pk__in=person.responsible_coordinator_ids()
    ).first()
    if coordinator is None:
        return ""
    return coordinator.get_full_name() or coordinator.email


def offer_placeholders(offer, person, language: str | None = None) -> dict[str, str]:
    """Values a template may interpolate. Everything is a string - a body is
    text, and ``None`` rendering as "None" in a worker's inbox is a bug.

    ``language`` is the *recipient's*, and it matters for more than the template
    row: ``get_wage_unit_display()`` resolves against whatever locale is active,
    which during a send is the sending staff member's. Without the override a
    Ukrainian worker's offer reads "8.50 EUR za hodinu" - Ukrainian body, Slovak
    wage unit - because the sender happened to be working in Slovak.
    """
    project = getattr(offer, "project", None)
    office = getattr(offer, "office", None)
    wage = ""
    if getattr(offer, "wage", None) is not None:
        wage = f"{offer.wage} {offer.currency}"
        if offer.wage_unit:
            with translation.override(language or settings.LANGUAGE_CODE):
                wage = f"{wage} {offer.get_wage_unit_display()}"
    return {
        "first_name": person.first_name or "",
        "last_name": person.last_name or "",
        "offer_title": offer.title or "",
        "project": str(project) if project else "",
        "office": str(office) if office else "",
        "location": offer.location or "",
        "wage": wage,
        "start_date": offer.start_date.isoformat() if offer.start_date else "",
        "terms": offer.terms or "",
        "coordinator": _coordinator_name(person),
    }


def pick_offer_template(kind: str, language: str) -> OfferEmailTemplate:
    """Best active template for ``kind``: exact language, then the site default,
    then any. Raises ``OfferTemplateMissing`` rather than sending an empty body."""
    active = OfferEmailTemplate.objects.filter(kind=kind, is_active=True)
    for candidate in (language, settings.LANGUAGE_CODE):
        template = active.filter(language=candidate).first()
        if template is not None:
            return template
    template = active.first()
    if template is None:
        raise OfferTemplateMissing(f"No active template for '{kind}'.")
    return template


def render_offer_email(offer, person, kind: str) -> tuple[str, str, str]:
    """Return ``(language, subject, body)`` for this offer/person/kind.

    Substitution is ``string.Template.safe_substitute``, not Django template
    rendering: these bodies are operator-authored text, which has no business
    reaching template internals, and ``safe_substitute`` leaves an unknown
    ``$token`` intact instead of raising halfway through a batch. The send
    views show a preview, which is where a typo'd token gets caught.
    """
    language = _offer_language(person)
    template = pick_offer_template(kind, language)
    # The template's own language, not the requested one: a fallback row means
    # the body is in some other language, and the interpolated values must match
    # the text around them rather than the recipient's unfulfilled preference.
    values = offer_placeholders(offer, person, template.language)
    subject = string.Template(template.subject).safe_substitute(values)
    body = string.Template(template.body).safe_substitute(values)
    return template.language, subject, body


def offer_email_block_reason(person):
    """Why this person cannot be emailed an offer, or "" if they can.

    One function so the panel, the bulk preview and the send path agree - a
    recipient shown as sendable and then blocked at send time is the kind of
    mismatch that gets explained away as a glitch. Returns a lazy translated
    string: it is shown to staff and also stored on the record.
    """
    if getattr(person, "email_opt_out", False):
        return _("This person has opted out of offer emails.")
    if person.lifecycle_status == LifecycleStatus.BLACKLISTED:
        return _("This person is blacklisted.")
    if not (person.email or "").strip():
        return _("This person has no email address on file.")
    return ""


def send_offer_email(
    offer, person, kind: str, *, actor=None, batch=None
) -> OutboundEmail:
    """Send one offer email and record it, whatever the outcome."""
    record = OutboundEmail.objects.create(
        person=person,
        offer=offer,
        batch=batch,
        kind=kind,
        to_email=(person.email or "").strip(),
        sent_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    try:
        # Worker state first: an opt-out or a blacklisted person must never
        # reach the allowlist check, let alone the mail server. (The SMS path
        # consults neither - an offer is exactly the message that must not go
        # to someone who asked us to stop, or who we blocked.)
        reason = offer_email_block_reason(person)
        if reason:
            raise OfferEmailBlocked(reason)
        assert_recipient_allowed(record.to_email)
        if not email_configured():
            raise EmailNotConfigured("Email delivery is not configured.")

        language, subject, body = render_offer_email(offer, person, kind)
        record.language = language
        record.subject = subject
        record.body = body
        sent = EmailMessage(subject=subject, body=body, to=[record.to_email]).send(
            fail_silently=False
        )
        if sent != 1:
            raise EmailSendError("The mail server accepted no recipients.")
        record.status = OutboundEmail.Status.SENT
    except (OfferEmailBlocked, EmailRecipientNotAllowed) as exc:
        record.status = OutboundEmail.Status.BLOCKED
        record.error = str(exc)[:300]
    except (EmailNotConfigured, EmailSendError, OfferTemplateMissing) as exc:
        record.status = OutboundEmail.Status.FAILED
        record.error = str(exc)[:300]
    except (OSError, SMTPException) as exc:
        record.status = OutboundEmail.Status.FAILED
        record.error = str(exc)[:300]
    record.save(update_fields=["language", "subject", "body", "status", "error"])
    record_event(
        actor,
        "offer_email.sent",
        target=record,
        status=record.status,
        to=record.to_email,
        offer=getattr(offer, "pk", None),
        batch=getattr(batch, "pk", None),
    )
    return record


def offer_batch_limit() -> int:
    return int(getattr(settings, "OFFER_EMAIL_BATCH_LIMIT", 100))


def send_offer_batch(offer, people, kind: str, *, actor=None) -> EmailBatch:
    """Send one offer to many people as a single auditable batch.

    ``people`` must already be office-scoped by the caller - this function
    deliberately does no scoping of its own, so that the boundary stays visible
    in the view where the request's user is in hand.
    """
    recipients = list(people[: offer_batch_limit()])
    with transaction.atomic():
        batch = EmailBatch.objects.create(
            offer=offer,
            kind=kind,
            recipient_count=len(recipients),
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
    # Sends happen outside the transaction on purpose: holding one open across
    # N network round-trips would keep a write lock for the length of the batch,
    # and a failure at recipient 40 must not erase the 39 already delivered.
    for person in recipients:
        send_offer_email(offer, person, kind, actor=actor, batch=batch)
    record_event(
        actor,
        "offer_email.batch_sent",
        target=batch,
        offer=getattr(offer, "pk", None),
        kind=kind,
        recipients=len(recipients),
    )
    return batch


def purge_offer_emails() -> int:
    """Delete offer-email records past their retention window.

    Registered with ``core.retention`` so this PII store is not born
    undocumented — `OutboundMessage` never was, and the messaging spec still
    carries "approved message/log retention" as an open item. The *period* here
    is a placeholder until the client approves one: the default is deliberately
    long enough not to destroy evidence, and the job is a no-op when the setting
    is zero or unset.
    """
    days = int(getattr(settings, "OFFER_EMAIL_RETENTION_DAYS", 0) or 0)
    if days <= 0:  # Unapproved retention: keep everything rather than guess.
        return 0
    cutoff = timezone.now() - datetime.timedelta(days=days)
    deleted, _ = OutboundEmail.objects.filter(created_at__lt=cutoff).delete()
    return deleted


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
