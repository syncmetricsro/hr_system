#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "static/vendor/htmx.min.js": "e209dda5c8235479f3166defc7750e1dbcd5a5c1808b7792fc2e6733768fb447",
    "static/vendor/alpine.min.js": "57b37d7cae9a27d965fdae4adcc844245dfdc407e655aee85dcfff3a08036a3f",
    "static/vendor/licenses/htmx-LICENSE": "d3d2456f76414f2456104660ebd65aff1c04cd7966b942bdabd63f3cdb316a38",
    "static/vendor/licenses/alpine-LICENSE.md": "08b7502da6e7aa1d0bbdc97d220fbf669b9366c61bd0f072238283c89bc4773a",
    "static/vendor/chart.min.js": "84d0e233daba702b8f77d669d8c137cad36d441a10f200b6f2d3ab553bdfcf6b",
    "static/vendor/licenses/chartjs-LICENSE": "41a84aa2caba645f966a18d9c2056b73e6d3a81d80bc0046bc0011a2634d4cce",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"{relative}: missing")
            continue
        actual = sha256(path)
        if actual != expected:
            failures.append(f"{relative}: expected {expected}, got {actual}")

    if failures:
        print("Vendor asset verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Vendor assets verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
