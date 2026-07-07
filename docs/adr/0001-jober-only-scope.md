# ADR 0001: Jober-Only Scope

Status: **Superseded by [ADR 0021](0021-stage-b-extraction.md) (activated 2026-07-07).**
The single-client rule is replaced by ADR 0021's build discipline: client-agnostic
`core/`, switchable `features/`, per-client `clients/` layers, dependencies
pointing feature → core only. Historical text below is unchanged.

Previous status: Accepted

## Context

The production app is for Jober only. Historical demos and older plans contain CorvinumEU and shared-platform assumptions.

## Decision

Build one Jober application. Do not add client switching, Corvinum references, white-label abstractions, or shared-client data models.

## Consequences

The old demo may inform visual design, but production navigation, models, tests, and deployment remain Jober-specific.
