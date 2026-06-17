# ADR 0006: npm Exclusion

Status: Accepted

## Context

The dependency surface must stay small and auditable.

## Decision

Do not add Node.js, npm, pnpm, yarn, React, Vite, package files, JavaScript lockfiles, or `node_modules`.

## Consequences

CI and local checks fail if forbidden artifacts appear. Browser tests use Python Playwright, not JavaScript tooling.
