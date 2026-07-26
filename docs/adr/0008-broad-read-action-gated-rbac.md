# ADR 0008: Broad Read, Action-Gated RBAC

Status: Accepted — **amended by [ADR 0026](0026-office-scoped-rbac.md)**

> The "broad read" here is broad *within the viewer's offices*. ADR 0026 made
> `Office` a real access boundary: only Observer reads across offices, and
> direct access to another office's record returns 403. The four roles and the
> action-gating model below are unchanged.

## Context

Jober confirmed broad internal read visibility with role-gated actions.

## Decision

Use four roles: Recruiter, Coordinator, Manager/Admin, and Observer. Gate sensitive actions server-side and audit old/new values.

## Consequences

No arbitrary per-user permission matrix is introduced in MVP. Sensitive exceptions must be documented explicitly.
