# ADR 0014: Playwright Python Test Image

Status: Accepted

## Context

The hash-pinned Python test lock can install `playwright==1.60.0`, but Chromium cannot launch in the slim Python image because required browser system libraries such as `libglib-2.0.so.0` are absent.

The production runtime image must stay browser-free and Node/npm-free.

## Decision

Use the official Playwright Python image for browser tests only:

```text
mcr.microsoft.com/playwright/python:v1.60.0-noble
mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384
```

The test image version matches the locked Python package `playwright==1.60.0`.

The test-runner image is built from `Dockerfile.playwright-python`, installs project test dependencies from `requirements/test.lock` with `pip install --require-hashes`, then runs as a non-root `jober-tests` user.

`scripts/playwright_smoke.sh` creates an internal Docker network with no outbound route, then connects:
- the production app image as `jober-phase0-app`;
- the digest-pinned PostgreSQL test container as `jober-phase0-pw-db`;
- the Playwright test-runner container.

The browser reaches the app at `http://jober-phase0-app:8000`. It does not use host networking, `localhost`, or the default bridge.

`scripts/playwright_smoke.sh` checks that `node`, `npm`, `pnpm`, and `yarn` are not on `PATH` in the test image before running browser tests. It also checks `requirements/test.lock` pins `playwright==1.60.0` to match the image tag.

## Consequences

Playwright browsers and browser OS libraries remain test-only.

The production image continues to use the slim digest-pinned Python image and is verified by `scripts/check_production_image.sh` to contain no Node/npm artifacts, no Tailwind binary, no browser binaries, no Playwright Python package, and no Playwright image reference in Docker history.

The rejected alternative is building a custom browser-test image from `python:3.12-slim` with Debian browser libraries. Revisit that only if the official Playwright Python image introduces Node/npm on `PATH`, loses version lockstep with the Python package, or becomes operationally unacceptable for CI.
