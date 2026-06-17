# ADR 0013: Tailwind Fetch And Verify

Status: Accepted

## Context

The Phase 0 shell originally used a workstation Tailwind standalone CLI at `/home/disane/.local/bin/tailwindcss`. That proved the local build, but it made the production build depend on a host binary.

`AGENTS.md` requires the Docker/CI build to fetch Tailwind standalone CLI from the pinned official release URL, verify SHA-256 before execution, fail closed on mismatch, and exclude the binary from the runtime image.

## Decision

Pin Tailwind standalone CLI to official Tailwind Labs release `v4.3.0`, asset `tailwindcss-linux-x64`.

The expected SHA-256 comes from the official release `sha256sums.txt`, not from hashing a local copy:

```text
73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400  ./tailwindcss-linux-x64
```

The checksum is committed in `vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256`.

The Dockerfile has a dedicated `tailwind` build stage that:
- downloads the official `sha256sums.txt` from `https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.0/sha256sums.txt`;
- verifies that the official Linux x64 line matches the committed expected checksum;
- downloads `https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.0/tailwindcss-linux-x64`;
- verifies the downloaded binary hash before execution;
- builds `static/dist/css/app.css`;
- copies only the built CSS into the final runtime image.

## Consequences

The production image build no longer reads `~/.local/bin/tailwindcss` or any host Tailwind path.

The runtime image contains compiled CSS, not the Tailwind binary.

The local `TAILWIND_BIN` override remains only for developer convenience and still verifies against the committed vendor checksum.

## Caveat

This verifies the binary against the checksum published with the same release. If a same-release compromise changed both the asset and `sha256sums.txt`, checksum verification alone would not detect it. A future hardening step can add GitHub artifact-attestation verification or an independently mirrored checksum approval process.
