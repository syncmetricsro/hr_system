# ADR 0018: Coordinator-activated, system-enforced readiness gate

Status: Accepted
Date: 2026-06-28

Modifies the activation model in `Product_Design.md` §11.6 / §12.4.

## Context

The plan made the **manager** the approver who moves a worker to `WORKING`: a
four-pillar readiness checklist plus an `ActivationApproval` (pending/approved/
rejected) decided by a manager. During Phase 1 requirements review (2026-06-28,
`docs/product/phase1-open-questions.md`), Jober said the **coordinator** places
workers and the **manager does not confirm each action**; the manager instead
wants an **alert system** for missing/expiring papers.

## Decision

- **The coordinator activates** a worker to `WORKING`; there is **no manual
  manager-approval step**.
- **The system enforces the readiness gate**: activation is blocked unless the
  required pillars are satisfied — **medical and gear are always required**;
  **accommodation and transport may be N/A** (with explicit reason). This keeps
  the data-integrity guarantee of the four-pillar gate without a human approver.
- `ActivationApproval` becomes an **activation record** (who activated, when,
  readiness snapshot) for audit, not a manager approve/reject object.
- The **CARGO manager override** (§11.6) still stands: a manager may set a person
  to `WORKING` bypassing the gate, audited.
- Manager oversight is delivered by **alerts** (missing/expiring papers), mapped
  to the planned compliance alerts (§11.9) — roadmap Phase 3. Phase 1 stores the
  relevant dates (entry-medical date, certificate expiry) as groundwork.

## Status of implementation

The Person + lifecycle + Project + ProjectAssignment spine is built. The
placement service (`apps.projects.services.activate_on_project`) performs the
assignment and the `WORKING` transition today; the **readiness-gate enforcement
and the alert layer attach when `ReadinessRecord` lands** (next Phase 1 slice).
The RBAC action `project.assign` is granted to coordinator + manager.

## Consequences

- Faster day-to-day flow (no approval bottleneck), integrity preserved by the
  system gate rather than a person.
- `permission-matrix.md` and the open-decisions/phase1-open-questions registers
  reflect this; the manager's role shifts from gatekeeper to alert-driven oversight.
