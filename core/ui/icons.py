"""Shared icon vocabulary for the {% icon %} template tag.

One entry per icon *concept*, mapped to each client's own rendering
mechanism: Jober's inline SVG sprite (``templates/partials/
jober_nav_icons.html``, symbol ids) and CorvinumEU's subsetted Material
Symbols web font (``clients/corvinum_eu/static/corvinum/fonts/
icon-names.txt``, ligature names). Adding a new concept here makes it
available to both clients from one call site instead of hand-authoring
markup twice.

Deliberately excludes a few concepts (search, filter, back, sign-out) that
have no matching ligature in CorvinumEU's current font subset — expanding
that subset needs a font-subsetting tool, which is a new build dependency
requiring its own AGENTS.md §3.1 approval, not a silent addition here.
"""

from __future__ import annotations

ICONS: dict[str, dict[str, str]] = {
    "add": {"svg": "add", "material": "add"},
    "edit": {"svg": "edit", "material": "edit"},
    "delete": {"svg": "delete", "material": "delete"},
    "archive": {"svg": "archive", "material": "work_off"},
    "recycle": {"svg": "recycle", "material": "undo"},
    "approve": {"svg": "approve", "material": "check_circle"},
    "reject": {"svg": "reject", "material": "close"},
    "export": {"svg": "export", "material": "download"},
    "issue": {"svg": "issue", "material": "upload"},
    "receive": {"svg": "receive", "material": "download"},
    "adjust": {"svg": "adjust", "material": "sync"},
    "save": {"svg": "save", "material": "cloud_done"},
    "invite": {"svg": "invite", "material": "mail"},
    "promote": {"svg": "promote", "material": "workspace_premium"},
    "warehouse": {"svg": "warehouse", "material": "precision_manufacturing"},
    # Office/site marker (ADR 0026 Phase B office-scope badge). Deliberately
    # reuses assets both clients already ship - Jober's existing location-pin
    # symbol and a ligature already present in CorvinumEU's font subset - so
    # this adds no sprite symbol and no font-subsetting step (see module
    # docstring: expanding the subset would be a new build dependency).
    "office": {"svg": "field", "material": "location_on"},
    "cert-health": {"svg": "cert-health", "material": "medical_services"},
    "cert-forklift": {"svg": "cert-forklift", "material": "forklift"},
    "cert-crane": {"svg": "cert-crane", "material": "construction"},
    "cert-welding": {"svg": "cert-welding", "material": "factory"},
    "cert-other": {"svg": "cert-other", "material": "badge"},
}
