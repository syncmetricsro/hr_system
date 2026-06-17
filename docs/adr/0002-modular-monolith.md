# ADR 0002: Modular Monolith

Status: Accepted

## Context

Jober needs a small internal system with strong consistency, auditability, and simple deployment.

## Decision

Use a Django modular monolith: apps split domains inside one codebase and one PostgreSQL database.

## Consequences

Cross-domain workflows can use transactions and direct service calls. Separate services are deferred until a concrete operational need appears.
