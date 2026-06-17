# ADR 0004: htmx And Alpine Constraints

Status: Accepted

## Context

The app needs responsive server-driven interactions without introducing a frontend build chain.

## Decision

Use vendored htmx for server-backed fragments and vendored Alpine only for narrow local UI state.

## Consequences

Every htmx action must work as a normal full-page request. Alpine never owns permissions, persistence, calculations, or workflow state.
