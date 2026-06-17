#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import stat
import sys
import urllib.request
from pathlib import Path

RELEASE_BASE = "https://github.com/tailwindlabs/tailwindcss/releases/download"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"GET {url} returned HTTP {response.status}")
        output.write_bytes(response.read())


def expected_hash(path: Path, asset: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        digest, name = parts
        if name in {asset, f"./{asset}"}:
            return digest
    raise RuntimeError(f"{path} does not contain an expected hash for {asset}")


def official_hash(path: Path, asset: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        digest, name = parts
        if name in {asset, f"./{asset}"}:
            return digest
    raise RuntimeError(f"Official sha256sums.txt does not contain {asset}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and verify Tailwind standalone CLI.")
    parser.add_argument("--version", required=True, help="Tailwind release version without leading v, for example 4.3.0")
    parser.add_argument("--asset", required=True, help="Release asset name, for example tailwindcss-linux-x64")
    parser.add_argument("--expected-sha-file", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    tag = f"v{args.version}"
    expected = expected_hash(args.expected_sha_file, args.asset)
    checksums_url = f"{RELEASE_BASE}/{tag}/sha256sums.txt"
    asset_url = f"{RELEASE_BASE}/{tag}/{args.asset}"
    checksums_path = args.output.with_suffix(".sha256sums.txt")

    download(checksums_url, checksums_path)
    official = official_hash(checksums_path, args.asset)
    if official != expected:
        print(
            f"Tailwind official checksum mismatch for {args.asset}: expected manifest {expected}, official release {official}",
            file=sys.stderr,
        )
        return 1

    download(asset_url, args.output)
    actual = sha256(args.output)
    if actual != expected:
        print(
            f"Tailwind binary checksum mismatch for {args.asset}: expected {expected}, actual {actual}",
            file=sys.stderr,
        )
        return 1

    current_mode = args.output.stat().st_mode
    args.output.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Verified Tailwind {tag} {args.asset} ({actual})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
