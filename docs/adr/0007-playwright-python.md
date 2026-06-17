# ADR 0007: Playwright Python

Status: Accepted

## Context

The app requires browser smoke tests, including mobile coordinator checks, while remaining npm-free.

## Decision

Use Playwright through PyPI and pytest in the test environment only.

## Consequences

Playwright browsers are installed only in test containers/CI. They are never present in the production runtime image.
