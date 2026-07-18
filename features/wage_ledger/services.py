from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext as _

from core.audit.services import record_event
from features.wage_ledger.models import WageEntry


@transaction.atomic
def record_wage(
    person,
    *,
    period: str,
    gross_amount,
    note: str = "",
    actor=None,
) -> WageEntry:
    try:
        amount = Decimal(str(gross_amount))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(_("Enter a valid gross amount.")) from exc

    entry = WageEntry(
        person=person,
        period=period,
        gross_amount=amount,
        note=note,
        created_by=actor if getattr(actor, "is_authenticated", False) else None,
    )
    entry.full_clean()
    try:
        entry.save()
    except IntegrityError as exc:
        raise ValidationError(
            _("A wage is already recorded for this person and period.")
        ) from exc
    record_event(
        actor,
        "wage.recorded",
        target=entry,
        person_id=person.pk,
        person=str(person),
        period=entry.period,
        gross_amount=str(entry.gross_amount),
        currency=entry.currency,
    )
    return entry


def wage_history(person):
    return person.wage_entries.select_related("created_by").order_by("-period", "-id")
