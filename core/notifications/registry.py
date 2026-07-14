from __future__ import annotations

from collections.abc import Callable, Iterable

from core.notifications.types import NotificationItem

NotificationProvider = Callable[[object], Iterable[NotificationItem]]

_alert_providers: list[NotificationProvider] = []


def register_alert_provider(provider: NotificationProvider) -> None:
    """Register a feature-owned, role-aware actionable-alert provider."""
    if provider not in _alert_providers:
        _alert_providers.append(provider)


def alert_items(request) -> list[NotificationItem]:
    items: list[NotificationItem] = []
    for provider in _alert_providers:
        items.extend(provider(request))
    return items
