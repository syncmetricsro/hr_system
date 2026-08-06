from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from scripts.compile_po import parse_po

REPO = Path(__file__).resolve().parent.parent
LANGUAGES = ("sk", "hu", "uk")
INTENTIONALLY_SHARED_TERMS = {
    "sk": {"Audit"},
    "hu": {"Audit"},
    "uk": set(),
}


def _help_msgids() -> set[str]:
    tree = ast.parse((REPO / "core/ui/help.py").read_text(encoding="utf-8"))
    messages = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }
    for template_name in ("help/article.html", "pages/help_index.html"):
        template = (REPO / "templates" / template_name).read_text(encoding="utf-8")
        messages.update(re.findall(r"""{%\s*trans\s+["']([^"']+)""", template))
    return messages


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_help_message_has_a_reviewed_nonempty_translation(language):
    po_path = REPO / "locale" / language / "LC_MESSAGES/django.po"
    catalog = parse_po(po_path.read_text(encoding="utf-8"))
    help_msgids = _help_msgids()

    # A canary, not a target: it fails when help text is added so the
    # translations cannot be forgotten. 210 -> 263 on 2026-08-04, when the
    # money and approval articles gained a per-field reference; 264 added the
    # first formula-free Excel boundary; 266 documents the complete current
    # Finance workflow (empty state, both write paths, workbooks, and export).
    assert len(help_msgids) == 266
    assert not (help_msgids - catalog.keys())
    assert all(catalog[msgid].strip() for msgid in help_msgids)
    unchanged = {msgid for msgid in help_msgids if catalog[msgid] == msgid}
    assert unchanged == INTENTIONALLY_SHARED_TERMS[language]
