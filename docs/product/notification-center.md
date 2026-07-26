# Floating notification center

The authenticated Jober and CorvinumEU shells show the same compact notification
center in the top-right of the usable workspace. It is an operational aid, not
an email or browser-push channel.

## Behavior

- **Problems** are recomputed from current role-gated work queues. Dismissing a
  problem hides that exact state for the current user; it returns if the source
  record changes and still needs attention.
- **Updates** come from append-only audit events created after the current login.
  The viewer's own events and authentication events are excluded because the
  normal three-second flash message already confirms their actions.
- Items contain only a localized action, a safe subject summary, time, and an
  authorized internal link. Audit reasons, unrestricted metadata, financial
  amounts, document identifiers, and restricted blacklist reasons are excluded.
- Coordinators are scoped to responsible projects/workers and recruiters to
  people they own. **Managers are no longer company-wide** — as of ADR 0026
  every non-Observer role is additionally bounded by its own office(s), so a
  manager's feed covers their office, not the company. A record with no
  resolvable office follows the same rule the person views use: it belongs to
  its owning recruiter (`core/offices/scoping.py`). Observers do not receive
  the operational panel in v1.

## Refresh and delivery

The panel renders on every normal page response. A mutation made through htmx
emits `notificationsChanged`, which refreshes the panel fragment, and the panel
also offers a manual refresh control. There is no timer, polling loop, service
worker, WebSocket, or background browser request.

An update made by another user therefore appears on the viewer's next navigation,
form response, or manual refresh. If idle-browser realtime delivery becomes a
confirmed requirement, it needs a separate ADR covering ASGI/SSE or WebSockets,
Gunicorn/Dokku topology, connection limits, proxy timeouts, and monitoring.

## Extension contract

Feature apps register role-aware alert providers through
`core.notifications.registry.register_alert_provider`. A provider returns
`NotificationItem` values with an opaque stable key and a version derived from
the underlying state. Providers must apply their feature flag, RBAC action, and
object scope before returning an item — and "object scope" now includes
**office scope**: filter through `user_office_scope` / `core/offices/scoping.py`
the same way the owning feature's own views do, or the panel becomes a way to
read another office's records by their titles. The server recomputes this list
before accepting a dismissal, so posted keys never grant visibility or access.
