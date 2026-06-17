#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_NAMES = {
    "package.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
    "yarn.lock",
    "node_modules",
}

FORBIDDEN_PREFIXES = {
    "vite.config.",
}

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "test-artifacts",
}


def is_forbidden(path: Path) -> bool:
    name = path.name
    return name in FORBIDDEN_NAMES or any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if is_forbidden(path):
            failures.append(str(path.relative_to(ROOT)))

    if failures:
        print("Forbidden Node/npm artifacts found:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("No forbidden Node/npm artifacts found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
