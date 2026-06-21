from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse


PROJECT_CARDS = [
    {
        "name": "DHL Bratislava",
        "coordinator": "Koordinátor A",
        "readiness": "3/4",
        "needs": "lekárska prehliadka",
    },
    {
        "name": "WEBASTO",
        "coordinator": "Koordinátor B",
        "readiness": "4/4",
        "needs": "pripravené",
    },
    {
        "name": "CARGO",
        "coordinator": "manažérsky override",
        "readiness": "2/4",
        "needs": "výstroj a doprava",
    },
]


def healthz(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


@login_required
def dashboard(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "projects": PROJECT_CARDS,
            "field_panel_open": False,
        },
    )


@login_required
def field_queue(request: HttpRequest) -> TemplateResponse:
    template = "partials/field_queue.html"
    context = {"projects": PROJECT_CARDS, "field_panel_open": True}
    if request.headers.get("HX-Request") == "true":
        return TemplateResponse(request, template, context)
    return TemplateResponse(request, "pages/dashboard.html", context)
