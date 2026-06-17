# Playwright Test Environment Note

Last updated: 2026-06-17

## What was tried

The test lock installs `playwright==1.60.0` and `pytest-playwright==0.8.0` inside the digest-pinned Python 3.12 container:

```text
python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9
```

`python -m playwright install chromium` downloaded the Playwright-pinned Chromium browser in that ephemeral test container.

## Result

Browser launch failed because the slim Python image does not include Chromium system libraries:

```text
error while loading shared libraries: libglib-2.0.so.0: cannot open shared object file
```

## Decision

Use the official Playwright Python test image, pinned by digest:

```text
mcr.microsoft.com/playwright/python:v1.60.0-noble@sha256:8ff591d613b01c884cc488339ed4318b4513eaf0c57a164a878ba49e70e3f384
```

This is test-only. The production runtime image remains browser-free and is checked separately.

Inspection result:

```text
node=not-found
npm=not-found
pnpm=not-found
yarn=not-found
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

`Dockerfile.playwright-python` installs the project test dependencies from the hash-pinned lock during test-image build.

`scripts/playwright_smoke.sh` starts the app, PostgreSQL, and test runner on a Docker network created with `--internal`, so the test has app/DB connectivity but no outbound internet route. The browser reaches the app by service hostname:

```text
http://jober-phase0-app:8000
```

The smoke covers `/healthz/`, the login page, and the mobile dashboard interaction.
