from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

URL_SCRIPT = """
import django
django.setup()
from django.urls import NoReverseMatch, reverse
from django.conf import settings as s

# CorvinumEU mounts equipment + blacklist + compliance…
reverse("equipment_reviews")
reverse("blacklist_queue")
reverse("compliance_list")
reverse("two_factor_setup")
reverse("checklist_item_toggle", args=[1])
reverse("ledger_overview")
reverse("payslip_list")
reverse("notification_panel")
reverse("notification_dismiss")
if "testserver" not in s.ALLOWED_HOSTS:
    s.ALLOWED_HOSTS.append("testserver")
from django.test import Client
from core.people.forms import PersonForm
assert s.SESSION_COOKIE_NAME == "corvinum_sessionid", s.SESSION_COOKIE_NAME
assert s.CSRF_COOKIE_NAME == "corvinum_csrftoken"
assert s.LANGUAGE_COOKIE_NAME == "corvinum_language"
assert s.CLIENT_DEFAULT_THEME == "dark"
assert s.CLIENT_THEME_STORAGE_KEY == "corvinum-theme"
assert s.BRAND_NAME == "CorvinumEU PeopleOps"
assert s.BRAND_LOGO == "corvinum/brand/corvinum-logo-v1.webp"
client = Client()
login = client.get(reverse("login"))
login_body = login.content.decode("utf-8")
assert 'data-client-brand="CorvinumEU PeopleOps"' in login_body
assert '/static/corvinum/brand/corvinum-logo-v1.webp' in login_body
assert "Jober" not in login_body
response = client.post(reverse("set_language"), {"language": "hu", "next": "/sk/people/"})
assert response["Location"] == "/hu/people/"
assert response.cookies["corvinum_language"].value == "hu"
client.cookies["corvinum_language"] = "sk"
response = client.post(reverse("set_language"), {"language": "sk", "next": "/hu/people/"})
assert response["Location"] == "/sk/people/"
assert response.cookies["corvinum_language"].value == "sk"
assert "email" in PersonForm.base_fields
assert "core.notifications" in s.INSTALLED_APPS
# …and must NOT mount finance, SMS, accommodation, transport, or trials.
for absent in ("finance_summary", "accommodation_list", "transport_trends", "trials_queue"):
    try:
        reverse(absent)
    except NoReverseMatch:
        continue
    raise SystemExit(f"URL {absent!r} should not be mounted for corvinum_eu")
print("ok")
"""

TEMPLATE_SCRIPT = """
import django
django.setup()
from django.template.loader import get_template

base = get_template("layouts/base.html")
assert base.origin.name.endswith("clients/corvinum_eu/templates/layouts/base.html")
source = base.origin.loader.get_contents(base.origin)
assert '{% include "partials/confirm_dialog.html" %}' in source
assert '{% include "notifications/panel.html" %}' in source
assert source.count('{% include "partials/theme_picker.html" %}') == 2
assert 'data-theme-default="{{ CLIENT_DEFAULT_THEME }}"' in source

dialog = get_template("partials/confirm_dialog.html")
dialog_source = dialog.origin.loader.get_contents(dialog.origin)
assert 'id="confirm-dialog"' in dialog_source
assert "data-confirm-cancel" in dialog_source
assert "data-confirm-agree" in dialog_source
print("ok")
"""


def _run(*argv: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update({
        "DJANGO_SETTINGS_MODULE": "clients.corvinum_eu.settings",
        "DJANGO_DEBUG": "1",
    })
    return subprocess.run(list(argv), capture_output=True, text=True, env=env, cwd=REPO)


def test_corvinum_client_boots():
    """Stage C (ADR 0022): the CorvinumEU thin client passes system checks."""
    result = _run(sys.executable, str(REPO / "manage.py"), "check")
    assert result.returncode == 0, result.stdout + result.stderr


def test_corvinum_demo_seed_command_is_registered():
    """The client demo app + its idempotent seed load under corvinum settings
    (no DB here — `--help` exercises import, registration, and argparse)."""
    result = _run(sys.executable, str(REPO / "manage.py"), "seed_corvinum_demo", "--help")
    assert result.returncode == 0, result.stdout + result.stderr


def test_corvinum_demo_bootstrap_seeds_intake_before_people_scenario():
    """A clean local demo must support Add person without a manual command."""
    source = (REPO / "scripts" / "corvinum_app.sh").read_text(encoding="utf-8")
    questionnaire = "manage seed_questionnaire"
    scenario = "manage seed_corvinum_demo"
    assert questionnaire in source
    assert source.index(questionnaire) < source.index(scenario)


def test_corvinum_demo_runner_keeps_smtp_secrets_in_web_runtime_only():
    """Provider credentials are opt-in and never enter migrations or seeds."""
    source = (REPO / "scripts" / "corvinum_app.sh").read_text(encoding="utf-8")
    manage_body = source.split("manage() {", 1)[1].split("print_access() {", 1)[0]
    app_run = source.split('docker run -d --name "$APP"', 1)[1]

    assert 'CONSOLE_EMAIL_ENV=(-e DJANGO_EMAIL_BACKEND=' in source
    assert '"${CONSOLE_EMAIL_ENV[@]}"' in manage_body
    assert '"${APP_EMAIL_ENV[@]}"' in app_run
    assert "-e DJANGO_EMAIL_HOST_PASSWORD" in source
    assert "SMTP delivery requested" in source


def test_corvinum_url_surface_matches_flag_set():
    """Flags decide the URL surface: equipment/blacklist/compliance mounted,
    Jober-only modules (finance, accommodation, transport, trials) absent."""
    result = _run(sys.executable, "-c", URL_SCRIPT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


def test_corvinum_shell_includes_shared_confirmation_dialog():
    result = _run(sys.executable, "-c", TEMPLATE_SCRIPT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout
