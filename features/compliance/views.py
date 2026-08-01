from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, require_action
from core.media import CertificateUploadError
from core.offices.scoping import assert_person_in_scope
from core.people.models import Person
from core.people.permissions import can_view_sensitive
from features.compliance.forms import CertificateForm, CertificateReasonForm
from features.compliance.models import (
    FILE_ALLOWED_CATEGORIES,
    Certificate,
    CertificateRecordStatus,
)
from features.compliance.services import (
    archive_certificate,
    compliance_alerts,
    purge_certificate_files,
    renew_certificate,
    save_certificate,
)


def _assert_certificate_access(user, person: Person) -> None:
    assert_person_in_scope(user, person)
    if not can_view_sensitive(user, person):
        raise PermissionDenied("Not permitted to manage this person's certificates.")


def _active_certificate(pk: int) -> Certificate:
    return get_object_or_404(
        Certificate.objects.select_related("person"),
        pk=pk,
        record_status=CertificateRecordStatus.ACTIVE,
    )


def _active_occupational_certificate(pk: int) -> Certificate:
    return get_object_or_404(
        Certificate.objects.select_related("person"),
        pk=pk,
        record_status=CertificateRecordStatus.ACTIVE,
        category__in=FILE_ALLOWED_CATEGORIES,
    )


@login_required
def compliance_list(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        "pages/compliance_list.html",
        {"alerts": compliance_alerts(request.user)},
    )


@require_action(Action.CERTIFICATE_MANAGE)
def certificate_create(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    _assert_certificate_access(request.user, person)
    form = CertificateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        certificate = form.save(commit=False)
        certificate.person = person
        try:
            save_certificate(
                certificate,
                actor=request.user,
                front_upload=form.cleaned_data["front_upload"],
                back_upload=form.cleaned_data.get("back_upload"),
                creating=True,
            )
        except CertificateUploadError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, _("Certificate added."))
            return redirect("person_detail", pk=person.pk)
    return TemplateResponse(
        request, "pages/certificate_form.html", {"form": form, "person": person}
    )


@require_action(Action.CERTIFICATE_MANAGE)
def certificate_edit(request: HttpRequest, pk: int) -> HttpResponse:
    certificate = _active_occupational_certificate(pk)
    person = certificate.person
    _assert_certificate_access(request.user, person)
    form = CertificateForm(
        request.POST or None, request.FILES or None, instance=certificate
    )
    if request.method == "POST" and form.is_valid():
        certificate = form.save(commit=False)
        try:
            save_certificate(
                certificate,
                actor=request.user,
                front_upload=form.cleaned_data.get("front_upload"),
                back_upload=form.cleaned_data.get("back_upload"),
                remove_back=form.cleaned_data.get("remove_back", False),
                creating=False,
            )
        except CertificateUploadError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, _("Certificate updated."))
            return redirect("person_detail", pk=person.pk)
    return TemplateResponse(
        request,
        "pages/certificate_form.html",
        {"form": form, "person": person, "certificate": certificate},
    )


@require_action(Action.CERTIFICATE_MANAGE)
def certificate_renew(request: HttpRequest, pk: int) -> HttpResponse:
    previous = _active_occupational_certificate(pk)
    person = previous.person
    _assert_certificate_access(request.user, person)
    replacement = Certificate(
        person=person,
        category=previous.category,
        name=previous.name,
        issuer=previous.issuer,
    )
    form = CertificateForm(
        request.POST or None,
        request.FILES or None,
        instance=replacement,
        locked_category=previous.category,
    )
    if request.method == "POST" and form.is_valid():
        replacement = form.save(commit=False)
        try:
            renew_certificate(
                previous,
                replacement,
                actor=request.user,
                front_upload=form.cleaned_data["front_upload"],
                back_upload=form.cleaned_data.get("back_upload"),
            )
        except (CertificateUploadError, ValueError) as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, _("Certificate renewed."))
            return redirect("person_detail", pk=person.pk)
    return TemplateResponse(
        request,
        "pages/certificate_form.html",
        {
            "form": form,
            "person": person,
            "renewing": previous,
        },
    )


@require_action(Action.CERTIFICATE_MANAGE)
def certificate_archive(request: HttpRequest, pk: int) -> HttpResponse:
    certificate = _active_certificate(pk)
    _assert_certificate_access(request.user, certificate.person)
    form = CertificateReasonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        archive_certificate(
            certificate, actor=request.user, reason=form.cleaned_data["reason"]
        )
        messages.success(request, _("Certificate archived."))
        return redirect("person_detail", pk=certificate.person_id)
    return TemplateResponse(
        request,
        "pages/certificate_action.html",
        {"form": form, "certificate": certificate, "action": "archive"},
    )


@require_action(Action.CERTIFICATE_PURGE_FILE)
def certificate_purge_files(request: HttpRequest, pk: int) -> HttpResponse:
    certificate = get_object_or_404(Certificate.objects.select_related("person"), pk=pk)
    _assert_certificate_access(request.user, certificate.person)
    form = CertificateReasonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        purge_certificate_files(
            certificate, actor=request.user, reason=form.cleaned_data["reason"]
        )
        messages.success(request, _("Certificate files permanently removed."))
        return redirect("person_detail", pk=certificate.person_id)
    if request.method == "POST":
        return TemplateResponse(
            request,
            "pages/certificate_action.html",
            {"form": form, "certificate": certificate, "action": "purge"},
            status=400,
        )
    return TemplateResponse(
        request,
        "pages/certificate_action.html",
        {"form": form, "certificate": certificate, "action": "purge"},
    )
