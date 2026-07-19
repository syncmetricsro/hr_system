from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can, require_action
from core.people.models import Person
from features.payslips.models import Payslip
from features.payslips.services import PayslipError, record_payslip, send_payslip


@require_action(Action.PAYSLIP_VIEW)
def payslip_list(request):
    if request.method == "POST":
        if not can(request.user, Action.PAYSLIP_MANAGE):
            raise PermissionDenied
        person = get_object_or_404(Person, pk=request.POST.get("person"))
        try:
            record_payslip(
                person,
                period=request.POST.get("period", "").strip(),
                net_amount=request.POST.get("net_amount"),
                note=request.POST.get("note", "").strip(),
                actor=request.user,
            )
            messages.success(request, _("Payslip recorded."))
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
        return redirect("payslip_list")

    return render(request, "pages/payslips.html", {
        "payslips": Payslip.objects.select_related("person")[:100],
        "people": Person.objects.order_by("last_name", "first_name"),
        "may_manage": can(request.user, Action.PAYSLIP_MANAGE),
    })


@require_action(Action.PAYSLIP_MANAGE)
def payslip_send(request, pk: int):
    if request.method != "POST":
        return redirect("payslip_list")
    payslip = get_object_or_404(Payslip.objects.select_related("person"), pk=pk)
    try:
        password = send_payslip(payslip, actor=request.user)
    except PayslipError as exc:
        messages.error(request, str(exc))
    else:
        # One-time display for out-of-band delivery (ADR 0023): the password
        # exists only in this flash message, nowhere else.
        messages.success(
            request,
            _("Payslip emailed to %(to)s. One-time password (tell the worker by "
              "phone/Messenger, NOT email): %(pw)s")
            % {"to": payslip.sent_to, "pw": password},
        )
    return redirect("payslip_list")
