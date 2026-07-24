"""In-app Help area content registry (docs/product/help-area-design.md).

Hand-authored Django templates, not Markdown - avoids a new PyPI dependency
(AGENTS.md §3.1) and reuses the existing {% trans %}/{% blocktrans %} i18n
mechanism directly. No database model: content isn't user-editable.
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
            {"slug": "compliance", "title": _("Compliance: certificates and expiry alerts")},
        ],
    },
    {
        "label": _("Logistics"),
        "articles": [
            {"slug": "logistics", "title": _("Logistics: accommodation, equipment, and transport")},
        ],
    },
    {
        "label": _("Finance"),
        "articles": [
            {"slug": "finance", "title": _("Finance: recording a month and reading the reports")},
        ],
    },
    {
        "label": _("Feedback"),
        "articles": [
            {"slug": "feedback", "title": _("Feedback: links, QR codes, and submissions")},
        ],
    },
    {
        "label": _("Blacklist"),
        "articles": [
            {"slug": "blacklist", "title": _("Blacklist: proposing and deciding a case")},
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
