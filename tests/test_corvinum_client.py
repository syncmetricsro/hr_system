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

# CorvinumEU mounts equipment + blacklist + compliance…
reverse("equipment_reviews")
reverse("blacklist_queue")
reverse("compliance_list")
reverse("two_factor_setup")
reverse("checklist_item_toggle", args=[1])
# …and must NOT mount finance, SMS, accommodation, transport, or trials.
for absent in ("finance_summary", "accommodation_list", "transport_trends", "trials_queue"):
    try:
        reverse(absent)
    except NoReverseMatch:
        continue
    raise SystemExit(f"URL {absent!r} should not be mounted for corvinum_eu")
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


def test_corvinum_url_surface_matches_flag_set():
    """Flags decide the URL surface: equipment/blacklist/compliance mounted,
    Jober-only modules (finance, accommodation, transport, trials) absent."""
    result = _run(sys.executable, "-c", URL_SCRIPT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout
