# ADR 0003: Django Server Rendering

Status: Accepted

## Context

The project forbids SPA frameworks and needs robust permissions, forms, localization, and audit.

## Decision

Django owns routing, rendering, validation, authorization, workflow state, and persistence.

## Consequences

Browser JSON APIs are not added for normal UI. JSON endpoints need a separate approved integration reason.
