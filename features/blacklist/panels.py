"""Person-card + intake-form contributions of the blacklist feature."""

from __future__ import annotations

from django import forms
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from core.accounts.permissions import Action
from core.accounts.permissions import can as user_can
from features.blacklist.models import BlacklistCategory, IdentifierType
from features.blacklist.services import (
    check_matches,
    compute_composite_identifier,
    has_open_case,
    propose_case,
)
from core.ui.registry import flag_enabled


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
            "mothers_maiden_name": forms.CharField(
                label=_("Mother's maiden name (blacklist check)"), required=False,
                widget=forms.TextInput(attrs={"autocomplete": "off"}),
                help_text=_("Used only to compute a re-entry check; never stored."),
            ),
        }

    def post_create(self, request, person, cleaned):
        if not flag_enabled("duplicate_blacklist"):
            return
        identifier = cleaned.get("identifier")
        composite = compute_composite_identifier(
            person.first_name, person.last_name, person.date_of_birth,
            cleaned.get("mothers_maiden_name") or "",
        )
        candidates = {}
        if identifier:
            candidates[cleaned.get("identifier_type") or "national_id"] = identifier
        if composite:
            candidates[IdentifierType.NAME_DOB_MMN] = composite
        if not candidates:
            return
        matched_types = sorted(
            set(check_matches(candidates).values_list("identifier_type", flat=True))
        )
        if matched_types:
            propose_case(
                person,
                reason=f"Auto: intake re-entry match ({', '.join(matched_types)})",
                identifier=identifier or None,
                identifier_type=cleaned.get("identifier_type") or "national_id",
                composite_identifier=composite,
                actor=getattr(request, "user", None),
            )
            if request is not None:
                labels = dict(IdentifierType.choices)
                messages.warning(
                    request,
                    _("Possible blacklist match (%(types)s) — flagged for manager review. Activation is blocked until resolved.")
                    % {"types": ", ".join(str(labels.get(t, t)) for t in matched_types)},
                )
