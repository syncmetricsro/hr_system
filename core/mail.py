"""Whether, and to whom, this environment may send email.

Two features send mail to a worker and they are never installed together:
``features.messaging`` sends structured job offers (ADR 0029) and
``features.payslips`` sends encrypted PDFs (CorvinumEU only, ADR 0023). Neither
can import the other — CorvinumEU installs payslips and not messaging, so that
import would raise on the one client that most needs the guard — so the rule
lives once here, like ``core.media`` does for the shared upload pipeline.

The risk this exists for is the same one ``SMS_ALLOWED_RECIPIENTS`` answers for
Twilio: a staging app carries real credentials and fictional worker data, and a
fictional person record with a real address typed into it is indistinguishable
from any other. "The data is fake" is not a control.
"""

from __future__ import annotations

from django.conf import settings
from django.utils.translation import gettext_lazy as _

#: Feature flags whose features can email a worker. Consulted only by the
#: deploy check in ``core.checks``; add a third here when one appears.
WORKER_EMAIL_FLAGS = ("offer_emails", "payslips")


class EmailRecipientNotAllowed(Exception):
    """A non-production allowlist stopped a send before the mail server."""


def allowed_recipients() -> list[str]:
    """The configured allowlist. **Empty means unrestricted** — production's
    setting, and the reason this cannot simply be made mandatory."""
    return list(getattr(settings, "EMAIL_ALLOWED_RECIPIENTS", []) or [])


def _domain_of(address: str) -> str:
    """The domain part, taken from the **last** ``@``.

    Splitting on the first one would let a quoted local part smuggle a domain
    in: ``"a@jober.sk"@evil.test`` is an address at *evil.test*.
    """
    _local, separator, domain = (address or "").strip().casefold().rpartition("@")
    return domain if separator else ""


def _split_entries(allowed):
    """Sort the configured entries into exact addresses and domain rules.

    An entry beginning with ``@`` is a whole domain; anything else is an exact
    address, which is what every entry was before 2026-08-09.
    """
    exact, domains = set(), set()
    for raw in allowed:
        entry = (raw or "").strip().casefold()
        if not entry:
            continue
        if entry.startswith("@"):
            domain = entry[1:]
            # A bare "@" must match nothing. Read as "any domain" it would
            # silently unrestrict the environment - the opposite of what
            # somebody typing into an allowlist intends.
            if domain:
                domains.add(domain)
            continue
        exact.add(entry)
    return exact, domains


def recipient_allowed(address: str) -> bool:
    """Whether this environment may email ``address``.

    Entries are exact addresses or, since 2026-08-09, whole domains written as
    ``@example.com``. Domain matching is **exact**: ``@jober.sk`` allows
    ``anna@jober.sk`` and refuses ``anna@mail.jober.sk``. Subdomain matching
    would make the blast radius invisible - every present and future subdomain
    becomes sendable without the setting changing - so a subdomain is listed
    separately when it is wanted.
    """
    allowed = allowed_recipients()
    if not allowed:
        return True
    candidate = (address or "").strip().casefold()
    exact, domains = _split_entries(allowed)
    if candidate in exact:
        return True
    domain = _domain_of(candidate)
    return bool(domain) and domain in domains


def assert_recipient_allowed(address: str) -> None:
    """Raise :class:`EmailRecipientNotAllowed` unless this environment may email
    ``address``. Callers put this **before** any side effect - generating a
    password or a PDF for a send that is about to be refused is worse than
    wasteful, because the artefact then exists without a corresponding email."""
    if not recipient_allowed(address):
        # Name the address. The likeliest refusal is a subdomain somebody
        # assumed a domain entry covered, and "some address was refused" sends
        # them to the logs; this sends them to the setting. The allowlist
        # itself stays out of a user-facing string - it belongs in the deploy
        # check, which the operator reads and the office does not.
        raise EmailRecipientNotAllowed(
            _(
                "This environment may only email its configured test "
                "addresses; %(address)s is not one of them."
            )
            % {"address": (address or "").strip()}
        )


def email_configured() -> bool:
    """Whether a send could actually leave the process.

    The console and locmem backends cannot fail, so they count as configured -
    otherwise every local demo and every test would render its send control as
    "unavailable". Only the real SMTP backend needs checking. Exposed so the UI
    can *say* email is unavailable rather than offer a button that files a
    failure, the same reason ``sms_configured`` exists.
    """
    backend = (getattr(settings, "EMAIL_BACKEND", "") or "").strip()
    if not backend:
        # An empty EMAIL_BACKEND is not "some harmless backend that cannot
        # fail" - Django cannot import it, so every send raises ImportError.
        # Found on Jober staging 2026-08-03, where DJANGO_EMAIL_BACKEND was an
        # empty string sitting beside live SMTP credentials: the UI would have
        # offered a Send button and every press would have errored.
        return False
    if "smtp" not in backend:
        return True
    # Django's SMTP backend accepts STARTTLS or implicit SSL, never both. Keep
    # the UI and direct-send guards fail-closed instead of calling a backend
    # configuration that can only raise at delivery time.
    if bool(getattr(settings, "EMAIL_USE_TLS", False)) and bool(
        getattr(settings, "EMAIL_USE_SSL", False)
    ):
        return False
    # `localhost` is not a mail server anyone chose - it is the os.getenv
    # fallback in config/settings/base.py, i.e. "nobody set this". Treating it
    # as configured made every unconfigured environment offer a Send button and
    # then fail against a refused connection on port 587, which is precisely the
    # dishonest state this function exists to prevent. An environment genuinely
    # relaying through a local MTA sets DJANGO_EMAIL_HOST explicitly to
    # 127.0.0.1 or its hostname.
    host = (getattr(settings, "EMAIL_HOST", "") or "").strip()
    if host in ("", "localhost"):
        return False
    return bool(getattr(settings, "DEFAULT_FROM_EMAIL", ""))
