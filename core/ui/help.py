"""In-app Help area content registry (docs/product/help-area-design.md).

Hand-authored Django templates, not Markdown - avoids a new PyPI dependency
(AGENTS.md §3.1) and reuses the existing {% trans %}/{% blocktrans %} i18n
mechanism directly. No database model: content isn't user-editable.

**Articles are gated by the same feature flags as the navigation.** Without
this, a CorvinumEU user was offered - and could read - articles explaining
Feedback, Finance reports and accommodation, none of which that client's app
has. Documentation for a feature you cannot reach is worse than no
documentation: it reads as something broken or missing.

An article lists the flags it depends on; it appears when **any** of them is
on, because an article can legitimately cover several features (Logistics
covers accommodation, equipment and transport, and CorvinumEU has only the
middle one). An article with no flags is always available.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

HELP_GROUPS = [
    {
        "label": _("Getting started"),
        "articles": [
            {"slug": "getting-started", "title": _("Getting started")},
        ],
    },
    {
        "label": _("People"),
        "articles": [
            {"slug": "people", "title": _("People: intake, lifecycle, and trials")},
        ],
    },
    {
        "label": _("Projects"),
        "articles": [
            {"slug": "projects", "title": _("Projects: assignments and readiness")},
        ],
    },
    {
        "label": _("Compliance"),
        "articles": [
            {
                "slug": "compliance",
                "title": _("Compliance: certificates and expiry alerts"),
                "flags": ["documents"],
            },
        ],
    },
    {
        "label": _("Logistics"),
        "articles": [
            {
                "slug": "logistics",
                "title": _("Logistics: accommodation, equipment, and transport"),
                "flags": ["accommodation", "equipment", "transport"],
            },
        ],
    },
    {
        "label": _("Finance"),
        "articles": [
            {
                "slug": "finance",
                "title": _("Finance: recording a month and reading the reports"),
                "flags": ["profitability"],
            },
        ],
    },
    {
        "label": _("Feedback"),
        "articles": [
            {
                "slug": "feedback",
                "title": _("Feedback: links, QR codes, and submissions"),
                "flags": ["feedback"],
            },
        ],
    },
    {
        "label": _("Blacklist"),
        "articles": [
            {
                "slug": "blacklist",
                "title": _("Blacklist: proposing and deciding a case"),
                "flags": ["duplicate_blacklist"],
            },
        ],
    },
    {
        "label": _("Audit"),
        "articles": [
            {"slug": "audit", "title": _("Audit: what's logged and why")},
        ],
    },
]

ARTICLE_TEMPLATES = {
    article["slug"]: f"help/{article['slug']}.html"
    for group in HELP_GROUPS
    for article in group["articles"]
}


def article_is_available(article) -> bool:
    """True when this client has at least one of the features the article
    describes, or when it describes none in particular."""
    from core.ui.registry import flag_enabled

    flags = article.get("flags")
    if not flags:
        return True
    return any(flag_enabled(flag) for flag in flags)


def available_groups() -> list[dict]:
    """`HELP_GROUPS` with unavailable articles - and then empty groups -
    removed, for whichever client is running."""
    groups = []
    for group in HELP_GROUPS:
        articles = [a for a in group["articles"] if article_is_available(a)]
        if articles:
            groups.append({**group, "articles": articles})
    return groups
