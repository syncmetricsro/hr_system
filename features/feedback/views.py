from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action, user_office_scope
from core.offices.scoping import assert_office_in_scope
from core.ui.qr import qr_pdf, qr_svg
from features.feedback.models import FeedbackLink, FeedbackSubmission
from core.projects.forms import operable_projects
from core.audit.services import record_event


def _link_scope_q(user, prefix: str = "") -> Q | None:
    """Restrict feedback links to the viewer's offices (ADR 0026).

    A link is office-bound only through its project, and ``project`` is
    nullable - a link with no project is a company-wide poster, so it carries
    no office constraint. That differs from ``Person``, whose office-less
    fallback is its owning recruiter; a link has no owner to fall back to.
    """
    scope = user_office_scope(user)
    if scope is None:
        return None
    return Q(**{f"{prefix}project__isnull": True}) | Q(
        **{f"{prefix}project__office__in": scope}
    )


def _assert_link_in_scope(user, link) -> None:
    if link.project_id is None:
        return
    assert_office_in_scope(user, link.project.office_id)


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
                link=link,
                message=message,
                rating=int(rating) if rating.isdigit() else None,
            )
            record_event(None, "feedback.received", target=submission)
            submitted = True
        else:
            error = _("Message is required.")
    return TemplateResponse(
        request,
        "pages/feedback_form.html",
        {"link": link, "submitted": submitted, "error": error},
    )


@require_action(Action.FEEDBACK_VIEW)
def feedback_inbox(request: HttpRequest) -> HttpResponse:
    link_q = _link_scope_q(request.user)
    link_qs = FeedbackLink.objects.filter(is_active=True)
    submission_qs = FeedbackSubmission.objects.select_related("link", "link__project")
    if link_q is not None:
        link_qs = link_qs.filter(link_q)
        submission_qs = submission_qs.filter(_link_scope_q(request.user, "link__"))
    links = []
    for link in link_qs:
        url = request.build_absolute_uri(reverse("feedback_form", args=[link.token]))
        links.append({"link": link, "url": url, "qr_svg": qr_svg(url)})
    return TemplateResponse(
        request,
        "pages/feedback_inbox.html",
        {
            "submissions": submission_qs[:200],
            "links": links,
            # The picker must not offer a project the viewer cannot operate.
            "projects": operable_projects(request.user),
        },
    )


@require_action(Action.FEEDBACK_VIEW)
def feedback_link_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    """Downloadable, printable one-page flyer (QR + label + URL) for a
    feedback link - staff print it and post it where workers will see it
    (docs/product/feedback-flyer-design.md)."""
    link = get_object_or_404(FeedbackLink, pk=pk)
    _assert_link_in_scope(request.user, link)
    url = request.build_absolute_uri(reverse("feedback_form", args=[link.token]))
    pdf_bytes = qr_pdf(url, label=link.label)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="feedback-{link.token}.pdf"'
    )
    return response


@require_POST
@require_action(Action.FEEDBACK_VIEW)
def feedback_link_create(request: HttpRequest) -> HttpResponse:
    label = (request.POST.get("label") or "").strip()
    project_id = request.POST.get("project") or None
    if (
        project_id
        and not operable_projects(request.user).filter(pk=project_id).exists()
    ):
        # Posting another office's project id must not create a link there.
        raise PermissionDenied("This project belongs to another office.")
    if label:
        FeedbackLink.objects.create(label=label, project_id=project_id)
        messages.success(request, _("Feedback link created."))
    else:
        messages.error(request, _("Label is required."))
    return redirect("feedback_inbox")
