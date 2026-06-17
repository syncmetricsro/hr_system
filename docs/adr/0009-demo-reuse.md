# ADR 0009: Demo Reuse

Status: Accepted

## Context

The old static demo has useful Jober visual language but obsolete workflow and scope.

## Decision

Reuse visual patterns selectively: folder tabs, dense operational panels, mobile touch spacing, and Jober palette. Do not reuse removed modules or in-memory state architecture.

## Consequences

Production UI should feel related to the approved Jober demo while behaving as a Django server-rendered application.
