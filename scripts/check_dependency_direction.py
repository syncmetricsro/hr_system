#!/usr/bin/env python3
"""Stage B tripwire (ADR 0021): dependencies must point feature -> core only.

Scans python sources for `from apps.X`/`from core.X`/`from features.X` imports
and fails when a CORE app imports a FEATURE app. An explicit allowlist carries
the known pre-B1 debt; entries are removed as B1 lands, and a stale allowlist
entry (no longer occurring) also fails so the list can only shrink.

Usage: python3 scripts/check_dependency_direction.py
Exit 0 = clean (or only allowlisted debt). Exit 1 = violation or stale entry.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CORE = {"accounts", "audit", "people", "projects", "core", "ui", "retention"}
FEATURES = {
    "logistics", "finance", "intake", "messaging",
    "compliance", "feedback", "blacklist",
}

# Known pre-B1 debt: "owner_app:imported_app". Must shrink to empty by end of B1.
ALLOWLIST: set[str] = set()

IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(?:apps|core|features)\.([a-z_]+)", re.M)


def owning_app(path: Path) -> str | None:
    parts = path.parts
    for root in ("apps", "core", "features"):
        if root in parts:
            i = parts.index(root)
            if i + 1 < len(parts):
                return parts[i + 1]
    return None


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    found: set[str] = set()
    for root in ("apps", "core", "features"):
        base = repo / root
        if not base.exists():
            continue
        for py in base.rglob("*.py"):
            owner = owning_app(py.relative_to(repo))
            if owner not in CORE:
                continue
            text = py.read_text(encoding="utf-8")
            for imported in IMPORT_RE.findall(text):
                if imported in FEATURES:
                    found.add(f"{owner}:{imported}")

    violations = sorted(found - ALLOWLIST)
    stale = sorted(ALLOWLIST - found)
    for v in violations:
        print(f"VIOLATION core->feature: {v}")
    for s in stale:
        print(f"STALE allowlist entry (remove it): {s}")
    if violations or stale:
        return 1
    print(f"dependency direction OK ({len(found)} allowlisted debt(s) remaining)"
          if found else "dependency direction OK (no core->feature imports)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
