from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True, slots=True)
class NotificationItem:
    key: str
    version: str
    category: Literal["alert", "update"]
    severity: Literal["danger", "warning", "info"]
    title: str
    detail: str
    url: str
    created_at: datetime | None = None
