from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action
from core.ui.qr import qr_svg
from features.feedback.models import FeedbackLink, FeedbackSubmission
from core.projects.models import Project
from core.audit.services import record_event


def feedback_form(request: HttpRequest, token: str) -> HttpResponse:
    """Public, no-login worker feedback form (the QR target)."""
    link = get_object_or_404(FeedbackLink, token=token, is_active=True)
    error = ""
    submitted = False
    if request.method == "POST":
        message = (request.POST.get("message") or "").strip()
        rating = request.POST.get("rating") or ""
        if message:
            submission = FeedbackSubmission.objects.create(
                link=link, message=message, rating=int(rating) if rating.isdigit() else None
            )
            record_event(None, "feedback.received", target=submission)
            submitted = True
        else:
            error = _("Message is required.")
    return TemplateResponse(
        request, "pages/feedback_form.html", {"link": link, "submitted": submitted, "error": error}
    )


@require_action(Action.FEEDBACK_VIEW)
def feedback_inbox(request: HttpRequest) -> HttpResponse:
    links = []
    for link in FeedbackLink.objects.filter(is_active=True):
        url = request.build_absolute_uri(reverse("feedback_form", args=[link.token]))
        links.append({"link": link, "url": url, "qr_svg": qr_svg(url)})
    return TemplateResponse(
        request,
        "pages/feedback_inbox.html",
        {
            "submissions": FeedbackSubmission.objects.select_related("link", "link__project")[:200],
            "links": links,
            "projects": Project.objects.filter(is_active=True),
        },
    )


@require_POST
@require_action(Action.FEEDBACK_VIEW)
def feedback_link_create(request: HttpRequest) -> HttpResponse:
    label = (request.POST.get("label") or "").strip()
    if label:
        FeedbackLink.objects.create(label=label, project_id=(request.POST.get("project") or None))
        messages.success(request, _("Feedback link created."))
    else:
        messages.error(request, _("Label is required."))
    return redirect("feedback_inbox")
