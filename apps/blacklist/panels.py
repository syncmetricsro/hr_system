"""Person-card + intake-form contributions of the blacklist feature."""

from __future__ import annotations

from django import forms
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.accounts.permissions import Action
from apps.accounts.permissions import can as user_can
from apps.blacklist.models import BlacklistCategory
from apps.blacklist.services import check_match, has_open_case, propose_case
from apps.core.registry import flag_enabled


def open_case_banner(request, person):
    if not flag_enabled("duplicate_blacklist") or not has_open_case(person):
        return None
    return {}


def case_panel(request, person):
    if not flag_enabled("duplicate_blacklist"):
        return None
    case = person.blacklist_cases.select_related("category").first()
    can_propose = (
        user_can(request.user, Action.BLACKLIST_PROPOSE) and not has_open_case(person)
    )
    if case is None and not can_propose:
        return None
    return {
        "blacklist_case": case,
        "can_view_blacklist_reason": user_can(request.user, Action.BLACKLIST_VIEW_REASON),
        "can_propose_blacklist": can_propose,
        "blacklist_categories": BlacklistCategory.objects.filter(is_active=True),
    }


class IntakeMatchExtension:
    """Optional, never-persisted ID field on the intake form; on create it runs
    the HMAC re-entry check and auto-proposes a case on a match (plan §12.13)."""

    def fields(self):
        if not flag_enabled("duplicate_blacklist"):
            return {}
        return {
            "identifier": forms.CharField(
                label=_("ID number (blacklist check)"), required=False,
                widget=forms.TextInput(attrs={"autocomplete": "off"}),
            ),
            "identifier_type": forms.ChoiceField(
                label=_("ID type"), required=False,
                choices=[
                    ("national_id", _("National ID")),
                    ("passport", _("Passport")),
                    ("other", _("Other")),
                ],
            ),
        }

    def post_create(self, request, person, cleaned):
        identifier = cleaned.get("identifier")
        if not flag_enabled("duplicate_blacklist") or not identifier:
            return
        if check_match(identifier).exists():
            propose_case(
                person, reason="Auto: intake identifier match",
                identifier=identifier,
                identifier_type=cleaned.get("identifier_type") or "national_id",
                actor=request.user,
            )
            messages.warning(
                request,
                _("Possible blacklist match — flagged for manager review. Activation is blocked until resolved."),
            )
