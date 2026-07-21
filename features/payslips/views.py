from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can, require_action
from features.payslips.forms import PayslipForm
from features.payslips.models import Payslip
from features.payslips.services import PayslipError, record_payslip, send_payslip


@require_action(Action.PAYSLIP_VIEW)
def payslip_list(request):
    may_manage = can(request.user, Action.PAYSLIP_MANAGE)
    if request.method == "POST":
        if not may_manage:
            raise PermissionDenied("Role is not permitted to manage payslips")
        form = PayslipForm(request.POST)
        if form.is_valid():
            record_payslip(
                form.cleaned_data["person"],
                period=form.cleaned_data["period"],
                net_amount=form.cleaned_data["net_amount"],
                note=form.cleaned_data["note"],
                issue_date=form.cleaned_data["issue_date"],
                actor=request.user,
            )
            messages.success(request, _("Payslip recorded."))
            return redirect("payslip_list")
        status = 400
    else:
        form = PayslipForm() if may_manage else None
        status = 200

    return render(
        request,
        "pages/payslips.html",
        {
            "payslips": Payslip.objects.select_related("person")[:100],
            "form": form,
            "may_manage": may_manage,
        },
        status=status,
    )


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
