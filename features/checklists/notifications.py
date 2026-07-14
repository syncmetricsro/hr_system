from __future__ import annotations

import hashlib

from django.urls import reverse
from django.utils.translation import gettext as _

from core.accounts.models import Role
from core.accounts.permissions import Action, can
from core.notifications.types import NotificationItem
from core.ui.registry import flag_enabled
from features.checklists.models import PersonChecklistItem


def checklist_notification_provider(request):
    if not flag_enabled("checklists") or not can(request.user, Action.CHECKLIST_TICK):
        return []
    open_items = PersonChecklistItem.objects.filter(
        done=False,
        item_template__critical=True,
        person__is_archived=False,
    ).select_related("person", "item_template")
    if request.user.role == Role.COORDINATOR:
        open_items = open_items.filter(
            person__assignments__status="active",
            person__assignments__project__responsible_coordinators=request.user,
        )
    items_by_person: dict[int, list] = {}
    for item in open_items.distinct():
        items_by_person.setdefault(item.person_id, []).append(item)
    notifications = []
    for person_items in items_by_person.values():
        person = person_items[0].person
        state = "|".join(str(item.pk) for item in person_items)
        notifications.append(NotificationItem(
            key=f"checklist:{person.pk}",
            version=hashlib.sha256(state.encode()).hexdigest(),
            category="alert",
            severity="danger",
            title=str(_("Activation checklist is incomplete")),
            detail=str(_("%(person)s · %(count)s critical items") % {
                "person": person,
                "count": len(person_items),
            }),
            url=reverse("person_detail", kwargs={"pk": person.pk}),
        ))
    return notifications
