from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.accounts.models import Role
from core.accounts.permissions import Action, require_action
from features.messaging.models import InboundMessage, MessageTemplate
from features.messaging.services import send_sms, verify_twilio_signature
from core.people.models import Person


@require_POST
@require_action(Action.SMS_SEND)
def send_sms_view(request: HttpRequest, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)

    # Coordinator-scoped sending: a coordinator may only message people on their
    # own projects (messaging spec).
    if getattr(request.user, "role", None) == Role.COORDINATOR:
        if request.user.pk not in person.responsible_coordinator_ids():
            raise PermissionDenied("Coordinator may only message people on their projects.")

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
        messages.error(request, _("Message failed: %(error)s") % {"error": message.error})
    return redirect("person_detail", pk=person.pk)


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
