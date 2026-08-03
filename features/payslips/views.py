from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from core.accounts.permissions import Action, can, require_action
from core.mail import email_configured
from core.offices.scoping import assert_person_in_scope, scope_people
from features.payslips.forms import PayslipForm
from features.payslips.models import Payslip
from features.payslips.services import PayslipError, record_payslip, send_payslip


@require_action(Action.PAYSLIP_VIEW)
def payslip_list(request):
    may_manage = can(request.user, Action.PAYSLIP_MANAGE)
    if request.method == "POST":
        if not may_manage:
            raise PermissionDenied("Role is not permitted to manage payslips")
        form = PayslipForm(request.POST, user=request.user)
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
        form = PayslipForm(user=request.user) if may_manage else None
        status = 200

    # Net pay is restricted data (PAYSLIP_VIEW is a sensitive read), so the list
    # is scoped like every other person-derived queryset. Payslip has no office
    # of its own; it inherits the worker's, hence the `person__` prefix.
    payslips = scope_people(
        Payslip.objects.select_related("person"), request.user, prefix="person__"
    )

    return render(
        request,
        "pages/payslips.html",
        {
            "payslips": payslips[:100],
            "form": form,
            "may_manage": may_manage,
            # Say "unavailable" rather than offer a button that fails at the
            # mail server — the same choice the offer-email panel makes.
            "email_configured": email_configured(),
        },
        status=status,
    )


@require_action(Action.PAYSLIP_MANAGE)
def payslip_send(request, pk: int):
    if request.method != "POST":
        return redirect("payslip_list")
    payslip = get_object_or_404(Payslip.objects.select_related("person"), pk=pk)
    # Filtering the list is not a boundary (ADR 0026): this view takes a pk, so
    # without the assert a manager could email another office's worker their
    # payslip by typing the id. The send also mints a one-time password and
    # shows it, so an unguarded POST leaks more than the document.
    assert_person_in_scope(request.user, payslip.person)
    try:
        password = send_payslip(payslip, actor=request.user)
    except PayslipError as exc:
        messages.error(request, str(exc))
    else:
        # One-time display for out-of-band delivery (ADR 0023): the password
        # exists only in this flash message, nowhere else.
        messages.success(
            request,
            _(
                "Payslip emailed to %(to)s. One-time password (tell the worker by "
                "phone/Messenger, NOT email): %(pw)s"
            )
            % {"to": payslip.sent_to, "pw": password},
        )
    return redirect("payslip_list")
