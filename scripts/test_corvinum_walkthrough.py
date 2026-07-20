#!/usr/bin/env python3
"""Validate the CorvinumEU presenter walkthrough against a running demo.

The checker follows the 14-section manual route in
``docs/deployment/corvinum-demo-runbook.md``. It mutates fictional candidate,
trial, checklist, and catalogue data. Provider-backed payslip delivery is off
by default and requires an explicit approval environment variable.

Run from the repository's hash-pinned test environment:

    python scripts/test_corvinum_walkthrough.py --url http://localhost:8001

For a deliberately approved SMTP check, first confirm that Marek's current
address is the controlled test inbox, then set ``PROVIDER_TEST_APPROVED=1`` and
pass ``--send-email --payslip-period YYYY-MM``. The application, not this
script, receives SMTP credentials through Doppler or the approved staging
secret manager.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hmac
import os
import re
import struct
import subprocess
import sys
import time
from hashlib import sha1
from html import unescape

import requests

STEP_SECONDS = 30
DIGITS = 6
MANAGER_EMAIL = "hradmin@demo.corvinum.test"
OBSERVER_EMAIL = "observer@demo.corvinum.test"
DEMO_PASSWORD = "demo-corvinum-2026"


class WalkthroughFailure(RuntimeError):
    pass


def totp_at(secret_b32: str, timestamp: int) -> str:
    """Calculate an RFC 6238 code without logging the underlying secret."""
    key = base64.b32decode(secret_b32, casefold=True)
    counter = timestamp // STEP_SECONDS
    digest = hmac.new(key, struct.pack(">Q", counter), sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**DIGITS)).zfill(DIGITS)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WalkthroughFailure(message)


def get_csrf(session: requests.Session, text: str) -> str:
    cookie_csrf = session.cookies.get("corvinum_csrftoken")
    if cookie_csrf:
        return cookie_csrf
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', text)
    if match:
        return match.group(1)
    raise WalkthroughFailure("Could not find a CSRF token.")


def clean_text(value: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", value)).split())


def option_value(text: str, label: str) -> str:
    for value, body in re.findall(
        r'<option[^>]+value="([^"]+)"[^>]*>(.*?)</option>', text, re.S
    ):
        if label.casefold() in clean_text(body).casefold():
            return value
    raise WalkthroughFailure(f"Could not find select option containing {label!r}.")


def first_match(pattern: str, text: str, message: str) -> str:
    match = re.search(pattern, text, re.S)
    if not match:
        raise WalkthroughFailure(message)
    return match.group(1)


def fetch_local_secret() -> str | None:
    """Read the disposable local demo's TOTP secret without printing it."""
    command = [
        "docker",
        "exec",
        "corvinum-dev-app",
        "python",
        "manage.py",
        "shell",
        "-c",
        (
            "from core.accounts.models import User; "
            f"u=User.objects.get(email='{MANAGER_EMAIL}'); "
            "print(getattr(getattr(u, 'totp_device', None), 'secret', ''))"
        ),
    ]
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.DEVNULL, timeout=5, text=True
        )
    except (OSError, subprocess.SubprocessError):
        return None
    values = [line.strip() for line in output.splitlines()]
    return next(
        (value for value in reversed(values) if re.fullmatch(r"[A-Z2-7]{32}", value)),
        None,
    )


def login(
    session: requests.Session,
    base_url: str,
    email: str,
    *,
    totp_secret: str | None = None,
) -> requests.Response:
    login_url = f"{base_url}/sk/prihlasenie/"
    response = session.get(login_url, timeout=15)
    require(response.status_code == 200, f"Login GET returned {response.status_code}.")
    response = session.post(
        login_url,
        data={
            "csrfmiddlewaretoken": get_csrf(session, response.text),
            "email": email,
            "password": DEMO_PASSWORD,
        },
        headers={"Referer": login_url},
        allow_redirects=False,
        timeout=15,
    )
    require(response.status_code == 302, f"Login POST returned {response.status_code}.")

    location = response.headers.get("Location", "")
    if "/2fa/" not in location:
        return session.get(f"{base_url}{location}", timeout=15)

    next_url = f"{base_url}{location}"
    challenge = session.get(next_url, timeout=15)
    secret = totp_secret
    if "2fa/setup" in location:
        secret = first_match(
            r"(?:secret=|<code>)([A-Z2-7]{32})",
            challenge.text,
            "Could not read the fresh local TOTP setup secret.",
        )
    require(
        bool(secret),
        "Manager TOTP is enrolled; provide TOTP_SECRET through the approved secret scope.",
    )
    code = totp_at(secret or "", int(time.time()))
    return session.post(
        next_url,
        data={"csrfmiddlewaretoken": get_csrf(session, challenge.text), "code": code},
        headers={"Referer": next_url},
        allow_redirects=True,
        timeout=15,
    )


def find_person_id(session: requests.Session, base_url: str, name: str) -> int:
    response = session.get(f"{base_url}/sk/people/", params={"q": name}, timeout=15)
    person_id = first_match(
        r"/sk/people/(\d+)/", response.text, f"Could not find fictional person {name}."
    )
    return int(person_id)


def payslip_send_url(text: str, person_name: str, period: str) -> str | None:
    for row in re.findall(r"<tr>(.*?)</tr>", text, re.S):
        row_text = clean_text(row)
        if person_name in row_text and period in row_text:
            match = re.search(r'action="([^"]+/payslips/\d+/send/)"', row)
            if match:
                return unescape(match.group(1))
    return None


def verify_payslips(
    session: requests.Session,
    base_url: str,
    *,
    send_email: bool,
    period: str | None,
) -> None:
    url = f"{base_url}/sk/payslips/"
    response = session.get(url, timeout=15)
    require(
        response.status_code == 200 and "Payslips" in response.text,
        "Payslips unavailable.",
    )
    if not send_email:
        print("  PASS: payslip workspace loaded; provider send skipped by default.")
        return

    require(
        os.environ.get("PROVIDER_TEST_APPROVED") == "1",
        "--send-email requires PROVIDER_TEST_APPROVED=1 after controlled-recipient review.",
    )
    require(
        bool(period and re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period)),
        "A valid --payslip-period is required.",
    )
    marek_id = find_person_id(session, base_url, "Marek Skladník")
    send_path = payslip_send_url(response.text, "Marek Skladník", period or "")
    if send_path is None:
        response = session.post(
            url,
            data={
                "csrfmiddlewaretoken": get_csrf(session, response.text),
                "person": str(marek_id),
                "period": period,
                "net_amount": "1450.00",
                "note": "Automated fictional walkthrough",
            },
            headers={"Referer": url},
            allow_redirects=True,
            timeout=15,
        )
        send_path = payslip_send_url(response.text, "Marek Skladník", period or "")
    require(bool(send_path), "Could not locate the requested fictional payslip row.")
    send_url = (
        f"{base_url}{send_path}"
        if (send_path or "").startswith("/")
        else (send_path or "")
    )
    delivered = session.post(
        send_url,
        data={"csrfmiddlewaretoken": get_csrf(session, response.text)},
        headers={"Referer": url},
        allow_redirects=True,
        timeout=30,
    )
    require(
        delivered.status_code == 200, f"Payslip send returned {delivered.status_code}."
    )
    require(
        "One-time password" in delivered.text or "Jednorazové heslo" in delivered.text,
        "Payslip send did not display the one-time-password confirmation.",
    )
    print(
        "  PASS: encrypted payslip send confirmed; password intentionally not logged."
    )


def verify_wage_sources(session: requests.Session, base_url: str) -> None:
    wages = session.get(f"{base_url}/sk/wages/", timeout=15)
    require(wages.status_code == 200, "Gross-wage workspace unavailable.")
    wage_text = clean_text(wages.text)
    for period, gross in (("2026-06", "1920"), ("2026-07", "2050")):
        require(
            period in wage_text and gross in wage_text,
            f"Gross-wage fixture {period} / {gross}.00 is missing.",
        )

    marek_id = find_person_id(session, base_url, "Marek Skladník")
    detail = session.get(f"{base_url}/sk/people/{marek_id}/", timeout=15)
    require(detail.status_code == 200, "Marek's person overview is unavailable.")
    detail_text = clean_text(detail.text)
    for value in ("1920", "1450", "2050", "1540"):
        require(value in detail_text, f"Expected pay source {value}.00 is missing.")
    require(
        "Vypočítaná čistá mzda" not in detail_text and "Computed net" not in detail_text,
        "The overview incorrectly presents an unsupported computed-net value.",
    )
    require(
        "finance-delta-mismatch" not in detail.text,
        "The overview incorrectly marks gross-versus-net source values as a mismatch.",
    )
    print("  PASS: calendar-month gross and recorded-net fixtures align by period.")


def run_walkthrough(
    base_url: str,
    *,
    send_email: bool = False,
    payslip_period: str | None = None,
) -> bool:
    base_url = base_url.rstrip("/")
    manager = requests.Session()
    timestamp = int(time.time())
    candidate_last_name = f"Walkthrough-{timestamp}"

    try:
        print(f"Target URL: {base_url}")
        print("[1/14] Secure entry and client isolation")
        secret = os.environ.get("TOTP_SECRET")
        if not secret and ("localhost" in base_url or "127.0.0.1" in base_url):
            secret = fetch_local_secret()
        landing = login(manager, base_url, MANAGER_EMAIL, totp_secret=secret)
        require(
            landing.status_code == 200, "Manager did not reach the authenticated app."
        )
        require(
            "CorvinumEU" in landing.text and "Jober" not in landing.text,
            "Client shell isolation failed.",
        )

        print("[2/14] Reports dashboard")
        reports = manager.get(f"{base_url}/sk/reports/", timeout=15)
        require(
            reports.status_code == 200 and "Reporty" in reports.text,
            "Reports unavailable.",
        )

        print("[3/14] Projects and export boundary")
        projects = manager.get(f"{base_url}/sk/projects/", timeout=15)
        require(
            projects.status_code == 200 and "Alfa Metallwerk" in projects.text,
            "Projects unavailable.",
        )

        print("[4/14] Guided intake v4")
        start_url = f"{base_url}/sk/intake/start/"
        started = manager.post(
            start_url,
            data={"csrfmiddlewaretoken": get_csrf(manager, projects.text)},
            headers={"Referer": f"{base_url}/sk/people/"},
            allow_redirects=False,
            timeout=15,
        )
        require(
            started.status_code == 302, f"Intake start returned {started.status_code}."
        )
        intake_url = f"{base_url}{started.headers['Location']}"
        panel = manager.get(intake_url, timeout=15)
        manager.post(
            intake_url,
            data={
                "csrfmiddlewaretoken": get_csrf(manager, panel.text),
                "first_name": "Olena",
                "last_name": candidate_last_name,
                "date_of_birth": "1995-05-14",
                "place_of_birth": "Uzhhorod",
            },
            headers={"Referer": intake_url},
            timeout=15,
        )
        panel = manager.get(intake_url, timeout=15)
        manager.post(
            intake_url,
            data={
                "csrfmiddlewaretoken": get_csrf(manager, panel.text),
                "phone": "+421 900 000 999",
                "email": "",
                "address": "Fiktívna 15, Komárno",
                "nationality": "Ukrajina",
                "preferred_language": "sk",
            },
            headers={"Referer": intake_url},
            timeout=15,
        )
        panel = manager.get(intake_url, timeout=15)
        completed = manager.post(
            intake_url,
            data={
                "csrfmiddlewaretoken": get_csrf(manager, panel.text),
                "disability": "nie",
                "disability_type": "",
                "blacklist_identifier": "",
                "blacklist_identifier_type": "national_id",
                "blacklist_mothers_maiden_name": "",
            },
            headers={"Referer": intake_url},
            allow_redirects=False,
            timeout=15,
        )
        require(
            completed.status_code == 302, "Final intake panel did not create a person."
        )
        person_url = f"{base_url}{completed.headers['Location']}"
        person_id = int(person_url.rstrip("/").split("/")[-1])

        print("[5/14] Trial scheduling and outcome")
        person = manager.get(person_url, timeout=15)
        alfa_id = option_value(person.text, "Alfa Metallwerk")
        tomorrow = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%Y-%m-%dT08:00")
        manager.post(
            f"{base_url}/sk/people/{person_id}/assign-trial/",
            data={
                "csrfmiddlewaretoken": get_csrf(manager, person.text),
                "project": alfa_id,
                "scheduled_for": tomorrow,
                "note": "Automated fictional walkthrough",
            },
            headers={"Referer": person_url},
            timeout=15,
        )
        person = manager.get(person_url, timeout=15)
        trial_id = first_match(
            r"/sk/trials/(\d+)/outcome/",
            person.text,
            "Scheduled trial was not rendered.",
        )
        outcome = manager.post(
            f"{base_url}/sk/trials/{trial_id}/outcome/",
            data={
                "csrfmiddlewaretoken": get_csrf(manager, person.text),
                "outcome": "pass",
            },
            headers={"Referer": person_url},
            allow_redirects=True,
            timeout=15,
        )
        require(outcome.status_code == 200, "Trial outcome failed.")

        print("[6/14] Checklist and activation gate")
        checklist_id = first_match(
            r"/sk/checklist/(\d+)/toggle/",
            outcome.text,
            "No checklist item was rendered.",
        )
        toggled = manager.post(
            f"{base_url}/sk/checklist/{checklist_id}/toggle/",
            data={"csrfmiddlewaretoken": get_csrf(manager, outcome.text)},
            headers={"Referer": person_url},
            allow_redirects=True,
            timeout=15,
        )
        blocked = manager.post(
            f"{base_url}/sk/people/{person_id}/activate/",
            data={
                "csrfmiddlewaretoken": get_csrf(manager, toggled.text),
                "project": alfa_id,
            },
            headers={"Referer": person_url},
            allow_redirects=True,
            timeout=15,
        )
        require(
            "Trial day" in clean_text(blocked.text),
            "Open checklist did not block activation.",
        )

        print("[7/14] Notifications")
        notifications = manager.get(f"{base_url}/sk/notifications/", timeout=15)
        require(notifications.status_code == 200, "Notifications unavailable.")

        print("[8/14] Compliance")
        compliance = manager.get(f"{base_url}/sk/compliance/", timeout=15)
        require(
            compliance.status_code == 200 and "Compliance" in compliance.text,
            "Compliance unavailable.",
        )

        print("[9/14] Equipment catalogue")
        catalog_url = f"{base_url}/sk/equipment/catalog/new/"
        catalog = manager.get(catalog_url, timeout=15)
        created_item = manager.post(
            catalog_url,
            data={
                "csrfmiddlewaretoken": get_csrf(manager, catalog.text),
                "name": f"Walkthrough vest {timestamp}",
                "size": "L",
                "unit_price": "8.50",
                "is_active": "on",
            },
            headers={"Referer": catalog_url},
            allow_redirects=True,
            timeout=15,
        )
        require(created_item.status_code == 200, "Equipment catalogue creation failed.")

        print("[10/14] Ledger and CSV controls")
        ledger = manager.get(f"{base_url}/sk/ledger/", timeout=15)
        require(
            ledger.status_code == 200 and "Kniha záloh" in ledger.text,
            "Ledger unavailable.",
        )
        require(
            "Download CSV" in ledger.text or "Stiahnuť CSV" in ledger.text,
            "Ledger export missing.",
        )

        print("[11/14] Gross wage and payslip source reconciliation")
        verify_wage_sources(manager, base_url)

        print("[12/14] Payslip workspace")
        verify_payslips(
            manager,
            base_url,
            send_email=send_email,
            period=payslip_period,
        )

        print("[13/14] Audit")
        audit = manager.get(f"{base_url}/sk/audit/", timeout=15)
        require(
            audit.status_code == 200 and "Audit" in audit.text, "Audit unavailable."
        )

        print("[14/14] Observer read-only policy")
        observer = requests.Session()
        observer_home = login(observer, base_url, OBSERVER_EMAIL)
        require(observer_home.status_code == 200, "Observer login failed.")
        observer_ledger = observer.get(f"{base_url}/sk/ledger/", timeout=15)
        require(observer_ledger.status_code == 200, "Observer cannot read the ledger.")
        require(
            "Record entry" not in observer_ledger.text,
            "Observer received ledger mutation controls.",
        )
        observer_audit = observer.get(f"{base_url}/sk/audit/", timeout=15)
        require(observer_audit.status_code == 200, "Observer cannot read Audit.")
        verify_wage_sources(observer, base_url)

    except (requests.RequestException, WalkthroughFailure, ValueError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return False

    print("SUCCESS: all 14 Corvinum walkthrough sections passed.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=os.environ.get("TARGET_URL", "http://localhost:8001"),
        help="CorvinumEU base URL (default: local demo on port 8001)",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send/resend one encrypted fictional payslip after explicit approval",
    )
    parser.add_argument(
        "--payslip-period",
        help="YYYY-MM period to create or resend when --send-email is selected",
    )
    args = parser.parse_args()
    if args.send_email and not args.payslip_period:
        parser.error("--send-email requires --payslip-period YYYY-MM")
    if args.send_email and os.environ.get("PROVIDER_TEST_APPROVED") != "1":
        parser.error(
            "--send-email requires PROVIDER_TEST_APPROVED=1 after controlled-recipient review"
        )
    success = run_walkthrough(
        args.url,
        send_email=args.send_email,
        payslip_period=args.payslip_period,
    )
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()
