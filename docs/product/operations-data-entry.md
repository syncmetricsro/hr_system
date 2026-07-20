# Operations data entry

Jober's Trials, Transport, and Accommodation screens are operational
workspaces, not reporting-only destinations.

## Trials

Recruiters, coordinators, and managers may schedule an Available candidate for
an active project. Coordinators are limited to projects assigned to them. The
central Trials page supports candidate/project/date lookup, creation, and edits
to pending routing details. The candidate on an existing trial is immutable;
completed outcomes remain history.

## Transport

Coordinators record and edit weekly headcounts for their projects; managers may
operate every active project. A project/week pair is unique. Central creation
rejects duplicates explicitly, while the Project-detail quick entry retains its
idempotent update behavior. The Transport page combines record lookup with the
latest twelve-week company and project trends.

## Accommodation

Only managers maintain locations and rooms. Locations and rooms are retired by
deactivation, never hard-deleted. Active occupants block deactivation, and a
room's capacity cannot be reduced below its occupancy. Coordinators and managers
continue assigning and releasing workers; only active, non-full rooms in active
locations appear in the selector.

All mutations are server-authorized and audited. Normal form submissions are
the supported fallback; presentation enhancements must not be required for the
workflow to function.
