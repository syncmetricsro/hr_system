from __future__ import annotations

import json


class NotificationRefreshMiddleware:
    """Tell an htmx panel to refresh after an authenticated unsafe request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.headers.get("HX-Request") == "true"
            and request.method not in {"GET", "HEAD", "OPTIONS"}
            and getattr(getattr(request, "resolver_match", None), "url_name", None) != "notification_dismiss"
        ):
            existing = response.get("HX-Trigger")
            if existing:
                try:
                    payload = json.loads(existing)
                    if not isinstance(payload, dict):
                        payload = {str(payload): None}
                except json.JSONDecodeError:
                    payload = {name.strip(): None for name in existing.split(",") if name.strip()}
            else:
                payload = {}
            payload["notificationsChanged"] = None
            response["HX-Trigger"] = json.dumps(payload)
        return response
