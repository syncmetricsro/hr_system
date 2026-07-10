from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_core_boots_without_any_feature_or_client():
    """Stage D bar (ADR 0021): the core is self-sufficient. The synthetic
    _smoke client (no feature apps, neutral policies, all flags off) must pass
    Django's system checks — proving no core module hard-requires a feature."""
    env = dict(os.environ)
    env.update({
        "DJANGO_SETTINGS_MODULE": "clients._smoke.settings",
        "DJANGO_DEBUG": "1",
    })
    result = subprocess.run(
        [sys.executable, str(REPO / "manage.py"), "check"],
        capture_output=True, text=True, env=env, cwd=REPO,
    )
    assert result.returncode == 0, result.stdout + result.stderr
