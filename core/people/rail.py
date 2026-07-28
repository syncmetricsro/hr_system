"""The persistent worker status rail (J8).

The client asked for an always-visible list of workers and their current state,
live as the user navigates, with notifications in the same rail.

Two constraints shaped this:

* **It must not become an N+1 on every page render.** The rail's shell is
  static markup; its contents are fetched once per page through the same htmx
  pattern the notification centre already uses, so navigating does not
  re-aggregate anything server-side until the fragment is requested. One
  query serves the whole list.
* **The statuses are not hardcoded.** The brief says CorvinumEU's vocabulary is
  the candidate pipeline rather than working/not-working. Both clients in fact
  share `LifecycleStatus`, so rendering from its choices - through the same
  `status_pill` the People list uses - satisfies that by construction and
  cannot drift from the rest of the UI.

Scoping is `scope_people`, identical to the People list: a coordinator sees
their own people, a manager their office(s), an Observer everything.
"""

from __future__ import annotations

from core.offices.scoping import scope_people
from core.people.models import LifecycleStatus, Person

#: The rail is a glance, not a directory - People remains the place to browse.
#: Capped so one query stays cheap no matter how large the workforce grows.
RAIL_LIMIT = 60


def rail_people(request):
    """Workers visible to this user, most recently updated first."""
    people = scope_people(
        Person.objects.filter(is_archived=False), request.user
    ).only("id", "first_name", "last_name", "lifecycle_status", "avatar")
    return list(people.order_by("-updated_at", "last_name")[:RAIL_LIMIT])


def rail_context(request):
    """Everything the rail fragment needs, in one pass over one queryset."""
    people = rail_people(request)
    counts: dict[str, int] = {}
    for person in people:
        counts[person.lifecycle_status] = counts.get(person.lifecycle_status, 0) + 1
    return {
        "rail_people": people,
        # Driven by the lifecycle configuration, never a working/not-working
        # split - see the module docstring.
        "rail_status_counts": [
            {"value": value, "label": label, "count": counts.get(value, 0)}
            for value, label in LifecycleStatus.choices
            if counts.get(value)
        ],
        "rail_truncated": len(people) >= RAIL_LIMIT,
        "rail_limit": RAIL_LIMIT,
    }
