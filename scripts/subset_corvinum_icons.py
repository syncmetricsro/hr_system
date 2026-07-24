#!/usr/bin/env python3
"""Regenerate CorvinumEU's subsetted Material Symbols Outlined webfont.

Downloads the official variable font from google/material-design-icons,
pins it to the "24pt Regular" instance (FILL=0, GRAD=0, opsz=24 - matches
the currently-shipped subset's fvar, which keeps only wght variable), then
prunes its GSUB ligature table down to exactly the icon names
`icon-names.txt` lists, and writes a lean woff2 in place.

Why not a plain `fonttools subset --text=...` invocation: this font's GSUB
LigatureSubst table groups every ligature sharing the same first input
glyph into one LigatureSet. fonttools' text-driven closure retains the
WHOLE LigatureSet once anything in it matches - subsetting for a single
new word like "medical_services" alone pulled in 66 unrelated glyphs (the
entire "m..." group), and the full 49-name target list ballooned to 3335
glyphs this way. This script prunes the LigatureSubst.ligatures dict
directly at the data-structure level first (keeping only the exact
requested words), THEN runs a normal `fonttools subset --text-file` pass -
verified against the shipped file before any new names were added: 44
icons -> 70 glyphs both ways (this script reproduces the original exactly).

Usage (needs `brotli` for WOFF2 writing, not part of the app's own deps -
installed transiently, not added to requirements/*):
    docker run --rm -v "$PWD":/app -w /app --user "$(id -u):$(id -g)" \\
      jober-test:phase4 bash -c \\
      "pip install --quiet --user brotli && python3 scripts/subset_corvinum_icons.py"

To add a new icon: add its Material Symbols name to icon-names.txt, add
the matching entry to core/ui/icons.py's ICONS dict, re-run this script,
visually verify the new glyph renders, then record the new SHA-256 in
vendor/MANIFEST.md and scripts/verify_vendor_assets.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ICON_NAMES_FILE = REPO_ROOT / "clients/corvinum_eu/static/corvinum/fonts/icon-names.txt"
OUTPUT_FONT = REPO_ROOT / "clients/corvinum_eu/static/corvinum/fonts/material-symbols-outlined-subset.woff2"
SOURCE_URL = (
    "https://github.com/google/material-design-icons/raw/master/variablefont/"
    "MaterialSymbolsOutlined%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf"
)


def main() -> int:
    from fontTools.ttLib import TTFont

    names = [n.strip() for n in ICON_NAMES_FILE.read_text().splitlines() if n.strip()]
    print(f"Target: {len(names)} icon names from {ICON_NAMES_FILE}")

    work = REPO_ROOT / "_font_subset_work"
    work.mkdir(exist_ok=True)
    full_font_path = work / "MaterialSymbolsOutlined-full.ttf"
    if not full_font_path.exists():
        print("Downloading full variable font...")
        subprocess.run(
            ["curl", "-sL", "--max-time", "120", "-o", str(full_font_path), SOURCE_URL], check=True
        )

    instanced_path = work / "instanced.ttf"
    print("Instancing to FILL=0, GRAD=0, opsz=24 (wght stays variable)...")
    subprocess.run(
        [
            sys.executable, "-m", "fontTools.varLib.instancer",
            str(full_font_path), "FILL=0", "GRAD=0", "opsz=24",
            "-o", str(instanced_path),
        ],
        check=True,
    )

    font = TTFont(str(instanced_path))
    cmap = font.getBestCmap()
    gname_to_char = {gname: chr(cp) for cp, gname in cmap.items()}

    gsub = font["GSUB"].table
    lookup = gsub.LookupList.Lookup[0]
    matched: set[str] = set()
    target = set(names)

    for sub in lookup.SubTable:
        inner = sub.ExtSubTable
        new_ligatures = {}
        for first_glyph, lig_list in inner.ligatures.items():
            first_char = gname_to_char.get(first_glyph, "�")
            kept = []
            for lig in lig_list:
                rest = "".join(gname_to_char.get(g, "�") for g in lig.Component)
                word = first_char + rest
                if word in target:
                    kept.append(lig)
                    matched.add(word)
            if kept:
                new_ligatures[first_glyph] = kept
        inner.ligatures = new_ligatures

    missing = target - matched
    if missing:
        print(f"ERROR: {len(missing)} names not found in the source font: {sorted(missing)}", file=sys.stderr)
        return 1

    pruned_path = work / "pruned.ttf"
    font.save(str(pruned_path))

    text_path = work / "text.txt"
    text_path.write_text(" ".join(names))
    final_path = work / "final.ttf"
    subprocess.run(
        [
            sys.executable, "-m", "fontTools.subset", str(pruned_path),
            f"--text-file={text_path}", "--layout-features=rlig",
            f"--output-file={final_path}",
        ],
        check=True,
    )

    final = TTFont(str(final_path))
    final.flavor = "woff2"
    final.save(str(OUTPUT_FONT))
    print(f"Wrote {OUTPUT_FONT} ({OUTPUT_FONT.stat().st_size} bytes, {final['maxp'].numGlyphs} glyphs)")
    print("Next: visually verify the new icons render, then update vendor/MANIFEST.md's SHA-256.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
