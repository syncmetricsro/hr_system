from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.accounts.permissions import Action, require_action
from core.media import CertificateUploadError
from core.people.models import Person
from features.compliance.forms import CertificateForm
from features.compliance.models import Certificate
from features.compliance.services import compliance_alerts, delete_certificate, save_certificate


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
    form = CertificateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        certificate = form.save(commit=False)
        certificate.person = person
        uploaded = request.FILES.get("document")
        try:
            save_certificate(certificate, actor=request.user, uploaded_file=uploaded, creating=True)
        except CertificateUploadError as exc:
            messages.error(request, str(exc))
            return TemplateResponse(
                request, "pages/certificate_form.html", {"form": form, "person": person}
            )
        messages.success(request, _("Certificate added."))
        return redirect("person_detail", pk=person.pk)
    return TemplateResponse(request, "pages/certificate_form.html", {"form": form, "person": person})


@require_action(Action.CERTIFICATE_MANAGE)
def certificate_edit(request: HttpRequest, pk: int) -> HttpResponse:
    certificate = get_object_or_404(Certificate, pk=pk)
    person = certificate.person
    form = CertificateForm(request.POST or None, instance=certificate)
    if request.method == "POST" and form.is_valid():
        certificate = form.save(commit=False)
        uploaded = request.FILES.get("document")
        try:
            save_certificate(certificate, actor=request.user, uploaded_file=uploaded, creating=False)
        except CertificateUploadError as exc:
            messages.error(request, str(exc))
            return TemplateResponse(
                request, "pages/certificate_form.html", {"form": form, "person": person, "certificate": certificate}
            )
        messages.success(request, _("Certificate updated."))
        return redirect("person_detail", pk=person.pk)
    return TemplateResponse(
        request, "pages/certificate_form.html", {"form": form, "person": person, "certificate": certificate}
    )


@require_POST
@require_action(Action.CERTIFICATE_MANAGE)
def certificate_delete(request: HttpRequest, pk: int) -> HttpResponse:
    certificate = get_object_or_404(Certificate, pk=pk)
    person_pk = certificate.person_id
    delete_certificate(certificate, actor=request.user)
    messages.success(request, _("Certificate deleted."))
    return redirect("person_detail", pk=person_pk)
