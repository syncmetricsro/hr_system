"""Office-scope indicator for the shared shell (ADR 0026 Phase B).

Office scoping is enforced in every queryset and guarded with 403s, but that
is invisible on screen - a scoped manager just sees fewer rows, which reads
the same as an empty database. This surfaces *which* office(s) the current
view is limited to, so the boundary is legible rather than merely enforced.

Renders nothing at all on an install with no offices (CorvinumEU), keeping
the difference between clients a matter of data, not branching.
"""

from __future__ import annotations

from django.utils.translation import gettext as _

from core.accounts.permissions import user_office_scope


def office_scope(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"OFFICE_SCOPE_LABEL": "", "OFFICE_SCOPE_UNRESTRICTED": False}

    scope = user_office_scope(user)
    if scope is None:
        # Unrestricted: either a cross-office role (Observer/superuser) or an
        # install that does not use offices at all. Only the former should
        # advertise anything - the latter has no office concept to explain.
        from core.offices.models import Office

        if not Office.objects.exists():
            return {"OFFICE_SCOPE_LABEL": "", "OFFICE_SCOPE_UNRESTRICTED": False}
        return {
            "OFFICE_SCOPE_LABEL": _("All offices"),
            "OFFICE_SCOPE_UNRESTRICTED": True,
        }

    names = list(scope.order_by("name").values_list("name", flat=True))
    if not names:
        # Belongs to no office while offices exist: genuinely sees nothing.
        # Say so plainly rather than leaving an unexplained empty screen.
        return {
            "OFFICE_SCOPE_LABEL": _("No office"),
            "OFFICE_SCOPE_UNRESTRICTED": False,
        }
    if len(names) == 1:
        label = names[0]
    else:
        label = _("%(first)s +%(count)s") % {
            "first": names[0],
            "count": len(names) - 1,
        }
    return {"OFFICE_SCOPE_LABEL": label, "OFFICE_SCOPE_UNRESTRICTED": False}
