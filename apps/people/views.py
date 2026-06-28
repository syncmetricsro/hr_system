from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from apps.people.models import Person
from apps.people.permissions import can_view_sensitive


@login_required
def people_list(request: HttpRequest) -> TemplateResponse:
    # Broad internal read: any authenticated role may see the operational list.
    query = (request.GET.get("q") or "").strip()
    people = Person.objects.filter(is_archived=False)
    if query:
        people = people.filter(search_name__contains=query.lower())
    return TemplateResponse(
        request,
        "pages/people_list.html",
        {"people": people, "query": query},
    )


@login_required
def person_detail(request: HttpRequest, pk: int) -> TemplateResponse:
    person = get_object_or_404(Person, pk=pk)
    assignment = person.current_assignment()
    return TemplateResponse(
        request,
        "pages/person_detail.html",
        {
            "person": person,
            "assignment": assignment,
            # Sensitive fields (DOB, place of birth, disability) are only rendered
            # when the viewer is permitted (plan §8.1 / Q4).
            "show_sensitive": can_view_sensitive(request.user, person),
        },
    )
