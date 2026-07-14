from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import translate_url
from django.utils.translation import override
from django.views.i18n import LANGUAGE_QUERY_PARAMETER
from django.views.i18n import set_language as django_set_language

from core.accounts.models import Role
from core.ui import registry
from core.people.models import LifecycleStatus, Person
from core.people.services import inactive_by_reason
from core.projects.models import Project, TrialAssignment, TrialOutcome


def healthz(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


def set_language(request: HttpRequest) -> HttpResponse:
    """Keep Django's safe cookie behavior while reliably translating prefixes.

    Django's stock view resolves ``next`` using the language active on the
    unprefixed ``/i18n/setlang/`` request. If its cookie disagrees with a URL
    such as ``/hu/people/``, URL translation silently returns the original URL.
    Resolve once more under the source prefix so the selected language and URL
    cannot become stuck in disagreement.
    """
    response = django_set_language(request)
    if request.method != "POST":
        return response

    target_language = request.POST.get(LANGUAGE_QUERY_PARAMETER, "").lower()
    configured_languages = {code.lower() for code, _name in settings.LANGUAGES}
    location = response.headers.get("Location")
    if target_language not in configured_languages or not location:
        return response

    path = urlsplit(location).path
    source_language = path.lstrip("/").split("/", 1)[0].lower()
    if source_language not in configured_languages or source_language == target_language:
        return response

    with override(source_language):
        translated_location = translate_url(location, target_language)
    if translated_location != location:
        response.headers["Location"] = translated_location
    return response


@login_required
def reports(request: HttpRequest) -> TemplateResponse:
    """The single operational overview and drill-down reporting surface."""
    people = Person.objects.filter(is_archived=False)
    has_trials = registry.flag_enabled("recruitment_trials")
    pending_trials = TrialAssignment.objects.filter(outcome=TrialOutcome.PENDING)
    if getattr(request.user, "role", None) == Role.COORDINATOR:
        pending_trials = pending_trials.filter(project__responsible_coordinators=request.user)
    status_counts = [
        {
            "value": value,
            "label": label,
            "count": people.filter(lifecycle_status=value).count(),
        }
        for value, label in LifecycleStatus.choices
    ]
    return TemplateResponse(
        request,
        "pages/reports.html",
        {
            "active_projects": Project.objects.filter(is_active=True).count(),
            "total_people": people.count(),
            "pending_trials": pending_trials.count(),
            "has_trials": has_trials,
            "status_counts": status_counts,
            "inactive_by_reason": inactive_by_reason(),
            # Feature contributions (registered via the core registry).
            "report_tiles": registry.report_tiles(request),
            "report_panels": registry.report_panels(request),
        },
    )


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Compatibility route for the former separate Overview page."""
    return reports(request)
