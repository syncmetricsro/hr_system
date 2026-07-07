from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_no_unallowlisted_core_to_feature_imports():
    """Stage B tripwire (ADR 0021): core never imports features. The script's
    allowlist carries pre-B1 debt only and may only shrink."""
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "check_dependency_direction.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
