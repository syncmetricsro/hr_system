from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.accounts.models import Role
from core.accounts.permissions import Action, require_action, user_office_scope
from core.mail import email_configured
from core.offices.models import Office
from core.offices.scoping import (
    assert_office_in_scope,
    assert_person_in_scope,
    scope_people,
)
from core.projects.models import Project
from core.people.naming import fold_name
from features.messaging.forms import (
    BulkOfferConfirmForm,
    BulkOfferSelectionForm,
    JobOfferForm,
    OfferEmailTemplateForm,
    SendOfferEmailForm,
)
from features.messaging.models import (
    EmailBatch,
    InboundMessage,
    JobOffer,
    MessageTemplate,
    OfferEmailKind,
    OfferEmailTemplate,
    OutboundEmail,
)
from features.messaging.services import (
    OfferPreviewInvalid,
    OfferTemplateMissing,
    load_offer_batch_preview,
    offer_batch_limit,
    offer_email_block_reason,
    offer_email_selection_block_reason,
    render_offer_email,
    send_offer_batch,
    send_offer_email,
    send_sms,
    sign_offer_batch_preview,
    verify_twilio_signature,
)
from core.people.models import LifecycleStatus, Person


@require_POST
@require_action(Action.SMS_SEND)
def send_sms_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    # Office boundary first (ADR 0026): sending an SMS reaches a worker's
    # personal phone, so it needs the same 403 as viewing their record. The
    # person_detail page that renders this form is already scoped; this stops
    # a direct POST with another office's pk.
    assert_person_in_scope(request.user, person)

    # Coordinator-scoped sending: a coordinator may only message people on their
    # own projects (messaging spec). Narrower than the office boundary, not a
    # replacement for it.
    if getattr(request.user, "role", None) == Role.COORDINATOR:
        if request.user.pk not in person.responsible_coordinator_ids():
            raise PermissionDenied(
                "Coordinator may only message people on their projects."
            )

    if not person.phone:
        messages.error(request, _("This person has no phone number."))
        return redirect("person_detail", pk=person.pk)

    template_id = request.POST.get("template")
    if template_id:
        template = get_object_or_404(MessageTemplate, pk=template_id, is_active=True)
        body = template.body
    else:
        body = (request.POST.get("body") or "").strip()

    if not body:
        messages.error(request, _("Message body is required."))
        return redirect("person_detail", pk=person.pk)

    message = send_sms(person.phone, body, actor=request.user, person=person)
    if message.status == message.Status.SENT:
        messages.success(request, _("Message sent."))
    else:
        messages.error(
            request, _("Message failed: %(error)s") % {"error": message.error}
        )
    return redirect("person_detail", pk=person.pk)


# ---------------------------------------------------------------------------
# Offer emails (ADR 0029)
#
# Order in every view below, per the invariant stated in send_sms_view:
# @require_action first (role), then the office assert (object), then any
# feature-specific narrowing. Filtering a list is never a substitute for the
# object guard - someone can always type another office's pk into the URL.
# ---------------------------------------------------------------------------


# Shown beside the body field so an author does not have to guess the tokens.
_PLACEHOLDER_HELP = (
    "$first_name",
    "$last_name",
    "$offer_title",
    "$project",
    "$office",
    "$location",
    "$wage",
    "$start_date",
    "$terms",
    "$coordinator",
)


def _scoped_offers(user):
    """Offers the user may see. ``user_office_scope`` returns None for
    unrestricted roles, which means *do not filter* - not "all offices"."""
    offers = JobOffer.objects.select_related("project", "office")
    scope = user_office_scope(user)
    if scope is not None:
        offers = offers.filter(office__in=scope)
    return offers


def _assert_offer_in_scope(user, offer: JobOffer) -> None:
    assert_office_in_scope(user, offer.office)


def _scoped_offices(user):
    scope = user_office_scope(user)
    return Office.objects.all() if scope is None else scope


def _scoped_projects(user):
    projects = Project.objects.all()
    scope = user_office_scope(user)
    if scope is not None:
        projects = projects.filter(office__in=scope)
    return projects


def _assert_coordinator_may_message(user, person: Person) -> None:
    """A coordinator may only contact people on their own projects — the same
    narrowing SMS applies, and for the same reason."""
    if getattr(user, "role", None) == Role.COORDINATOR:
        if user.pk not in person.responsible_coordinator_ids():
            raise PermissionDenied(
                "Coordinator may only message people on their projects."
            )


@require_POST
@require_action(Action.OFFER_EMAIL_SEND)
def send_offer_email_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    assert_person_in_scope(request.user, person)
    _assert_coordinator_may_message(request.user, person)

    form = SendOfferEmailForm(
        request.POST, offer_queryset=_scoped_offers(request.user).filter(is_active=True)
    )
    if not form.is_valid():
        messages.error(request, _("Choose a job offer and an email type."))
        return redirect("person_detail", pk=person.pk)

    # The panel already hides the button for a blocked recipient; this stops a
    # direct POST, and says why rather than filing a mysterious failure.
    reason = offer_email_block_reason(person)
    if reason:
        messages.error(request, reason)
        return redirect("person_detail", pk=person.pk)

    record = send_offer_email(
        form.cleaned_data["offer"],
        person,
        form.cleaned_data["kind"],
        actor=request.user,
    )
    if record.status == OutboundEmail.Status.SENT:
        messages.success(request, _("Offer email sent."))
    else:
        messages.error(
            request, _("Offer email not sent: %(error)s") % {"error": record.error}
        )
    return redirect("person_detail", pk=person.pk)


@require_action(Action.OFFER_MANAGE)
def offer_list(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        "pages/offer_list.html",
        {
            "offers": _scoped_offers(request.user),
            "templates": OfferEmailTemplate.objects.all(),
            "email_configured": email_configured(),
        },
    )


@require_action(Action.OFFER_MANAGE)
def offer_create(request: HttpRequest) -> HttpResponse:
    form = JobOfferForm(
        request.POST or None,
        office_queryset=_scoped_offices(request.user),
        project_queryset=_scoped_projects(request.user),
    )
    if request.method == "POST" and form.is_valid():
        offer = form.save(commit=False)
        offer.created_by = request.user
        offer.save()
        messages.success(request, _("Job offer created."))
        return redirect("offer_list")
    return TemplateResponse(
        request, "pages/offer_form.html", {"form": form, "offer": None}
    )


@require_action(Action.OFFER_MANAGE)
def offer_edit(request: HttpRequest, pk: int) -> HttpResponse:
    offer = get_object_or_404(JobOffer, pk=pk)
    _assert_offer_in_scope(request.user, offer)
    form = JobOfferForm(
        request.POST or None,
        instance=offer,
        office_queryset=_scoped_offices(request.user),
        project_queryset=_scoped_projects(request.user),
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Job offer updated."))
        return redirect("offer_list")
    return TemplateResponse(
        request, "pages/offer_form.html", {"form": form, "offer": offer}
    )


@require_POST
@require_action(Action.OFFER_MANAGE)
def offer_archive(request: HttpRequest, pk: int) -> HttpResponse:
    offer = get_object_or_404(JobOffer, pk=pk)
    _assert_offer_in_scope(request.user, offer)
    offer.is_active = False
    offer.save(update_fields=["is_active"])
    messages.success(request, _("Job offer closed."))
    return redirect("offer_list")


def _bulk_recipients(
    user, offer: JobOffer, *, office=None, lifecycle_status="", query=""
):
    """Candidates for a bulk send, office-scoped.

    ``scope_people`` rather than a bare ``office__in``: a person with no office
    belongs to the recruiter who owns them, and that rule lives in one place.
    """
    people = scope_people(
        Person.objects.filter(is_archived=False).select_related("office"), user
    )
    if office is not None:
        people = people.filter(office=office)
    elif offer.office_id:
        people = people.filter(office_id=offer.office_id)
    if lifecycle_status in LifecycleStatus.values:
        people = people.filter(lifecycle_status=lifecycle_status)
    if query:
        folded = fold_name(query)
        lookup = Q(email__icontains=query) | Q(search_name__icontains=query.casefold())
        if folded:
            lookup |= Q(search_fold__contains=folded)
        people = people.filter(lookup)
    return people.order_by("last_name", "first_name")


def _bulk_filter_values(request: HttpRequest, offer: JobOffer):
    source = request.POST if request.method == "POST" else request.GET
    kind = source.get("kind") or OfferEmailKind.NEW_OFFER
    if kind not in OfferEmailKind.values:
        kind = OfferEmailKind.NEW_OFFER
    status = source.get("lifecycle_status") or ""
    if status not in LifecycleStatus.values:
        status = ""
    query = (source.get("q") or "").strip()[:255]
    office_pk = source.get("office") or ""
    office = None
    if office_pk:
        office = get_object_or_404(_scoped_offices(request.user), pk=office_pk)
    return kind, status, query, office_pk, office


def _recipient_rows(candidates):
    rows = []
    eligible_ids = []
    for person in candidates:
        reason = offer_email_selection_block_reason(person)
        eligible = not reason
        if eligible:
            eligible_ids.append(person.pk)
        rows.append({"person": person, "eligible": eligible, "reason": reason})
    return rows, eligible_ids


def _language_previews(offer, people, kind):
    labels = dict(settings.LANGUAGES)
    groups = {}
    for person in people:
        language, subject, body = render_offer_email(offer, person, kind)
        group = groups.setdefault(
            language,
            {
                "language": language,
                "language_label": labels.get(language, language),
                "count": 0,
                "person": person,
                "subject": subject,
                "body": body,
            },
        )
        group["count"] += 1
    return list(groups.values())


@require_action(Action.OFFER_EMAIL_BULK_SEND)
def offer_send_bulk(request: HttpRequest, pk: int) -> HttpResponse:
    """Select explicit recipients, then render the signed review step."""
    offer = get_object_or_404(JobOffer, pk=pk)
    _assert_offer_in_scope(request.user, offer)
    kind, status, query, office_pk, office = _bulk_filter_values(request, offer)
    candidates = _bulk_recipients(
        request.user,
        offer,
        office=office,
        lifecycle_status=status,
        query=query,
    )
    rows, eligible_ids = _recipient_rows(candidates)
    eligible = candidates.filter(pk__in=eligible_ids)
    limit = offer_batch_limit()
    form = BulkOfferSelectionForm(
        request.POST or None,
        office_queryset=_scoped_offices(request.user),
        recipient_queryset=eligible,
        status_choices=LifecycleStatus.choices,
        batch_limit=limit,
    )
    template_available = OfferEmailTemplate.objects.filter(
        kind=kind, is_active=True
    ).exists()
    configured = email_configured()

    if request.method == "POST":
        if not configured:
            form.add_error(None, _("Email is not configured in this environment."))
        if not template_available:
            form.add_error(None, _("No active template for this email type."))
        if form.is_valid() and configured and template_available:
            selected = list(
                form.cleaned_data["recipients"].order_by("last_name", "first_name")
            )
            try:
                previews = _language_previews(
                    offer, selected, form.cleaned_data["kind"]
                )
            except OfferTemplateMissing:
                form.add_error(None, _("No active template for this email type."))
            else:
                token = sign_offer_batch_preview(
                    offer, form.cleaned_data["kind"], selected, actor=request.user
                )
                return TemplateResponse(
                    request,
                    "pages/offer_send_bulk_preview.html",
                    {
                        "offer": offer,
                        "selected": selected,
                        "previews": previews,
                        "form": BulkOfferConfirmForm(initial={"preview_token": token}),
                    },
                )

    return TemplateResponse(
        request,
        "pages/offer_send_bulk.html",
        {
            "offer": offer,
            "form": form,
            "rows": rows,
            "eligible_count": len(eligible_ids),
            "limit": limit,
            "email_configured": configured,
            "template_available": template_available,
            "kinds": OfferEmailKind.choices,
            "statuses": LifecycleStatus.choices,
            "offices": _scoped_offices(request.user),
            "selected_kind": kind,
            "selected_status": status,
            "selected_office": office_pk,
            "query": query,
            "offer_office_label": offer.office,
        },
    )


@require_POST
@require_action(Action.OFFER_EMAIL_BULK_SEND)
def offer_send_bulk_confirm(request: HttpRequest, pk: int) -> HttpResponse:
    """Revalidate the signed preview, then execute it exactly once."""
    offer = get_object_or_404(JobOffer, pk=pk)
    _assert_offer_in_scope(request.user, offer)
    form = BulkOfferConfirmForm(request.POST)
    if not form.is_valid():
        messages.error(request, _("Review the recipients and email content first."))
        return redirect("offer_send_bulk", pk=offer.pk)
    try:
        payload = load_offer_batch_preview(
            form.cleaned_data["preview_token"], offer, actor=request.user
        )
    except OfferPreviewInvalid as exc:
        messages.error(request, str(exc))
        return redirect("offer_send_bulk", pk=offer.pk)

    existing = EmailBatch.objects.filter(request_token=payload["request_token"]).first()
    if existing is not None:
        return redirect("offer_batch_detail", pk=existing.pk)

    recipient_ids = payload["recipient_ids"]
    if len(recipient_ids) > offer_batch_limit():
        messages.error(request, _("The selected recipient list is too large."))
        return redirect("offer_send_bulk", pk=offer.pk)
    people = list(
        scope_people(
            Person.objects.filter(is_archived=False, pk__in=recipient_ids),
            request.user,
        ).order_by("last_name", "first_name")
    )
    if {person.pk for person in people} != set(recipient_ids):
        messages.error(
            request,
            _("The recipient list changed after preview. Review it again."),
        )
        return redirect("offer_send_bulk", pk=offer.pk)
    changed = [
        (person, offer_email_selection_block_reason(person)) for person in people
    ]
    changed = [(person, reason) for person, reason in changed if reason]
    if changed or not offer.is_active or not email_configured():
        messages.error(
            request,
            _("The recipient list changed after preview. Review it again."),
        )
        return redirect("offer_send_bulk", pk=offer.pk)
    try:
        _language_previews(offer, people, payload["kind"])
    except OfferTemplateMissing:
        messages.error(request, _("No active template for this email type."))
        return redirect("offer_send_bulk", pk=offer.pk)

    batch = send_offer_batch(
        offer,
        people,
        payload["kind"],
        actor=request.user,
        request_token=payload["request_token"],
    )
    return redirect("offer_batch_detail", pk=batch.pk)


@require_action(Action.OFFER_EMAIL_BULK_SEND)
def offer_batch_detail(request: HttpRequest, pk: int) -> TemplateResponse:
    batch = get_object_or_404(
        EmailBatch.objects.select_related("offer", "created_by"), pk=pk
    )
    if batch.offer is not None:
        _assert_offer_in_scope(request.user, batch.offer)
    emails = list(batch.emails.select_related("person"))
    if batch.offer is None:
        # Once the offer is gone, every outcome must still supply an office-
        # scoped person. An empty batch or a deleted person leaves no boundary
        # to prove, so fail closed instead of exposing a guessed batch ID.
        if not emails or any(email_record.person is None for email_record in emails):
            raise PermissionDenied
        for email_record in emails:
            assert_person_in_scope(request.user, email_record.person)
    counts = {status: 0 for status in OutboundEmail.Status.values}
    for email_record in emails:
        counts[email_record.status] += 1
    return TemplateResponse(
        request,
        "pages/offer_batch_detail.html",
        {
            "batch": batch,
            "emails": emails,
            "sent_count": counts[OutboundEmail.Status.SENT],
            "failed_count": counts[OutboundEmail.Status.FAILED],
            "blocked_count": counts[OutboundEmail.Status.BLOCKED],
            "queued_count": counts[OutboundEmail.Status.QUEUED],
            "complete": len(emails) == batch.recipient_count,
        },
    )


@require_action(Action.OFFER_TEMPLATE_MANAGE)
def offer_template_edit(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    template = get_object_or_404(OfferEmailTemplate, pk=pk) if pk else None
    form = OfferEmailTemplateForm(request.POST or None, instance=template)
    if request.method == "POST" and form.is_valid():
        saved = form.save(commit=False)
        if template is None:
            saved.created_by = request.user
        saved.save()
        messages.success(request, _("Template saved."))
        return redirect("offer_list")
    return TemplateResponse(
        request,
        "pages/offer_template_form.html",
        {"form": form, "template": template, "placeholders": _PLACEHOLDER_HELP},
    )


@csrf_exempt
@require_POST
def twilio_inbound(request: HttpRequest) -> HttpResponse:
    """Twilio inbound SMS webhook. Verifies the signature and fails closed."""
    url = request.build_absolute_uri()
    params = {key: request.POST[key] for key in request.POST}
    signature = request.headers.get("X-Twilio-Signature", "")
    if not verify_twilio_signature(url, params, signature):
        return HttpResponseForbidden("invalid signature")

    InboundMessage.objects.create(
        from_number=request.POST.get("From", ""),
        body=request.POST.get("Body", ""),
        provider_sid=request.POST.get("MessageSid", ""),
    )
    return HttpResponse("<Response></Response>", content_type="text/xml")
