# ADR 0001: Jober-Only Scope

Status: Accepted

## Context

The production app is for Jober only. Historical demos and older plans contain CorvinumEU and shared-platform assumptions.

## Decision

Build one Jober application. Do not add client switching, Corvinum references, white-label abstractions, or shared-client data models.

## Consequences

The old demo may inform visual design, but production navigation, models, tests, and deployment remain Jober-specific.
