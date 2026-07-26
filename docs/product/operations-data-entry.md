# Operations data entry

Jober's Trials, Transport, and Accommodation screens are operational
workspaces, not reporting-only destinations.

**All three are office-scoped (ADR 0026).** Every rule below applies *within*
the acting user's office(s): a non-Observer never sees, selects, or acts on
another office's project, room or worker, and reaching one by URL returns 403.
Observer spans all offices. The role rules stated per section are layered on
top of that boundary, not instead of it.

## Trials

Recruiters, coordinators, and managers may schedule an Available candidate for
an active project in their own office. Coordinators are additionally limited
to projects assigned to them. The central Trials page supports
candidate/project/date lookup, creation, and edits to pending routing
details. The candidate on an existing trial is immutable;
completed outcomes remain history.

## Transport

Coordinators record and edit weekly headcounts for their projects; managers may
operate every active project **in their office(s)**. A project/week pair is
unique. Central creation rejects duplicates explicitly, while the
Project-detail quick entry retains its idempotent update behavior. The
Transport page combines record lookup with the latest twelve-week company and
project trends.

## Accommodation

Only managers maintain locations and rooms. Locations and rooms are retired by
deactivation, never hard-deleted. Active occupants block deactivation, and a
room's capacity cannot be reduced below its occupancy. Coordinators and managers
continue assigning and releasing workers; only active, non-full rooms in active
locations **belonging to the acting user's office(s)** appear in the selector.

All mutations are server-authorized and audited. Normal form submissions are
the supported fallback; presentation enhancements must not be required for the
workflow to function.
