from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from django.utils.translation import gettext, override
REPO = Path(__file__).resolve().parent.parent

URL_SCRIPT = """
import django
django.setup()
from django.urls import NoReverseMatch, reverse
from django.conf import settings as s

# CorvinumEU mounts equipment + blacklist + compliance…
reverse("equipment_reviews")
reverse("equipment_catalog")
reverse("blacklist_queue")
reverse("compliance_list")
reverse("two_factor_setup")
reverse("checklist_item_toggle", args=[1])
reverse("archive_person", args=[1])
reverse("trials_queue")
reverse("trial_create")
reverse("ledger_overview")
reverse("payslip_list")
reverse("notification_panel")
reverse("notification_dismiss")
if "testserver" not in s.ALLOWED_HOSTS:
    s.ALLOWED_HOSTS.append("testserver")
from django.test import Client
from core.accounts.models import User
from core.accounts.permissions import Action, can
from core.people.forms import PersonForm
assert s.SESSION_COOKIE_NAME == "corvinum_sessionid", s.SESSION_COOKIE_NAME
assert s.CSRF_COOKIE_NAME == "corvinum_csrftoken"
assert s.LANGUAGE_COOKIE_NAME == "corvinum_language"
assert s.CLIENT_DEFAULT_THEME == "dark"
assert s.CLIENT_THEME_STORAGE_KEY == "corvinum-theme"
assert s.BRAND_NAME == "CorvinumEU PeopleOps"
assert s.BRAND_LOGO == "corvinum/brand/corvinum-logo-v1.webp"
assert can(User(role="manager"), Action.PERSON_ARCHIVE)
assert not can(User(role="coordinator"), Action.PERSON_ARCHIVE)
assert can(User(role="manager"), Action.INTAKE_ASSIGN_TRIAL)
assert can(User(role="coordinator"), Action.TRIAL_RECORD_OUTCOME)
assert can(User(role="manager"), Action.CATALOG_MANAGE)
assert not can(User(role="coordinator"), Action.CATALOG_MANAGE)
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
# …and must NOT mount finance, SMS, accommodation, or transport.
for absent in ("finance_summary", "accommodation_list", "transport_trends"):
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
    Jober-only modules (finance, accommodation, transport) absent; trials are
    enabled for CorvinumEU's candidate workflow."""
    result = _run(sys.executable, "-c", URL_SCRIPT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


def test_corvinum_shell_includes_shared_confirmation_dialog():
    result = _run(sys.executable, "-c", TEMPLATE_SCRIPT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


def test_corvinum_sidebar_uses_only_self_hosted_icon_glyphs():
    """A missing subset glyph renders its raw ligature name in the sidebar."""
    source = (
        REPO / "clients/corvinum_eu/templates/layouts/base.html"
    ).read_text(encoding="utf-8")
    available = set(
        (REPO / "clients/corvinum_eu/static/corvinum/fonts/icon-names.txt")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    used = set(re.findall(r'material-symbols-outlined" aria-hidden="true">([^<]+)<', source))
    assert used <= available


@pytest.mark.parametrize("language", ("sk", "hu", "uk"))
def test_equipment_catalogue_controls_are_translated(language):
    with override(language):
        assert gettext("Add equipment item") != "Add equipment item"
        assert gettext("Save equipment item") != "Save equipment item"
