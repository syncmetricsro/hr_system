# ADR 0015: Custom user model with email login and a single role field

Status: Accepted
Date: 2026-06-20

## Context

Phase 1 introduces authentication and the four fixed roles (Recruiter,
Coordinator, Manager/Administrator, Observer — plan §8). Until now the database
carried only Django contrib migrations; no business models and no users existed.
Swapping `AUTH_USER_MODEL` after users/relations exist is expensive, so the
decision must be made at the start of Phase 1.

The login surface designed in Phase 0 (`templates/pages/login.html`) collects an
**email** and password, not a username.

## Decision

- Add `apps.accounts.User` subclassing `AbstractUser`, with `username` removed,
  `email` as the unique `USERNAME_FIELD`, and a custom `UserManager`.
- Store the role as a single `role` field using `Role(TextChoices)`. We do **not**
  use Django groups/per-user permission matrices for product authorization
  (plan §8.2 "Do not implement per-user permission matrices in the MVP").
- Authorization is action-gated and layered on top in `apps/accounts/permissions.py`
  (see ADR 0008), not on the model.
- Set `AUTH_USER_MODEL = "accounts.User"` before any business module migration.

## Consequences

- Login matches the existing email-based template; no throwaway username field.
- A single `role` field keeps the matrix legible and testable, and mirrors
  `docs/permissions/jober-permission-matrix.md` one-to-one.
- Django admin uses a custom `UserAdmin` because the user is email-based.
- Future fine-grained needs (e.g. the open GDPR read-scope split) are handled by
  configuration/policy in `permissions.py`, not by reshaping the user model.
