# ADR 0005: Tailwind Standalone

Status: Accepted

## Context

The visual system should use Tailwind without Node/npm.

## Decision

Use Tailwind standalone CLI v4.3.0 from a human-approved, SHA-256-verified binary.

## Consequences

The binary is not committed and is excluded from runtime images. `TAILWIND_BIN` and `TAILWIND_SHA256` are required before execution.
