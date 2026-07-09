from __future__ import annotations

import csv

from django.http import HttpRequest, HttpResponse

from apps.accounts.permissions import Action, require_action
from apps.people.models import Person
from apps.projects.models import AssignmentStatus, Project

# Exports deliberately exclude bulk sensitive fields (DOB, disability, identifiers)
# — those stay on the per-person card behind can_view_sensitive, not in CSV dumps.


def csv_response(filename: str) -> tuple[HttpResponse, "csv._writer"]:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response, csv.writer(response)


@require_action(Action.EXPORT_APPROVED)
def people_csv(request: HttpRequest) -> HttpResponse:
    response, writer = csv_response("people.csv")
    writer.writerow(["last_name", "first_name", "status", "current_project", "owning_recruiter", "rehire_eligible"])
    people = Person.objects.filter(is_archived=False).select_related("owning_recruiter")
    for person in people:
        assignment = person.current_assignment()
        writer.writerow([
            person.last_name,
            person.first_name,
            person.get_lifecycle_status_display(),
            assignment.project.name if assignment else "",
            person.owning_recruiter.email if person.owning_recruiter else "",
            "yes" if person.rehire_eligible else "no",
        ])
    return response


@require_action(Action.EXPORT_APPROVED)
def projects_csv(request: HttpRequest) -> HttpResponse:
    response, writer = csv_response("projects.csv")
    writer.writerow(["code", "name", "partner", "office", "active", "financial_reporting", "active_workers"])
    for project in Project.objects.all():
        writer.writerow([
            project.code,
            project.name,
            project.partner,
            project.office,
            "yes" if project.is_active else "no",
            "yes" if project.financial_reporting_eligible else "no",
            project.assignments.filter(status=AssignmentStatus.ACTIVE).count(),
        ])
    return response
