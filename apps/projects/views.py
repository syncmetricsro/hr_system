from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from apps.projects.models import AssignmentStatus, Project


@login_required
def project_list(request: HttpRequest) -> TemplateResponse:
    projects = Project.objects.all().prefetch_related("responsible_coordinators")
    return TemplateResponse(request, "pages/project_list.html", {"projects": projects})


@login_required
def project_detail(request: HttpRequest, pk: int) -> TemplateResponse:
    project = get_object_or_404(
        Project.objects.prefetch_related("responsible_coordinators"), pk=pk
    )
    workers = (
        project.assignments.filter(status=AssignmentStatus.ACTIVE)
        .select_related("person")
        .order_by("person__last_name")
    )
    return TemplateResponse(
        request,
        "pages/project_detail.html",
        {"project": project, "workers": workers},
    )
