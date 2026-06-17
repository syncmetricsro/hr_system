# ADR 0008: Broad Read, Action-Gated RBAC

Status: Accepted

## Context

Jober confirmed broad internal read visibility with role-gated actions.

## Decision

Use four roles: Recruiter, Coordinator, Manager/Admin, and Observer. Gate sensitive actions server-side and audit old/new values.

## Consequences

No arbitrary per-user permission matrix is introduced in MVP. Sensitive exceptions must be documented explicitly.
