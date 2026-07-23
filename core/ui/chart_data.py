"""Shared chart payload shaping (ADR 0025).

Lives in core (not a feature app) because both core/ui/views.py and
features/finance/views.py need it, and core cannot import from features.
"""

from __future__ import annotations


def net_bar_payload(rows, *, label_key: str = "label", value_key: str = "net") -> dict:
    """{labels, net} shape for a horizontal diverging bar chart — the repeated
    shape behind the group/project/region breakdowns."""
    return {
        "labels": [r[label_key] for r in rows],
        "net": [r[value_key] for r in rows],
    }
