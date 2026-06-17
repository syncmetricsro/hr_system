# Tailwind Standalone CLI Provenance

Phase 0 pins Tailwind standalone CLI v4.3.0 for Linux x64.

Official release:
- Release: `https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.0`
- Binary asset: `https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.0/tailwindcss-linux-x64`
- Official checksum file: `https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.0/sha256sums.txt`
- Linux x64 checksum: `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400`

The expected checksum is recorded in `vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256`.

Local workstation artifact verified on 2026-06-17:
- Path: `/home/disane/.local/bin/tailwindcss`
- Reported version: `tailwindcss v4.3.0`
- Observed SHA-256: `73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400`
- Result: local binary matches the official Tailwind Labs Linux x64 checksum.

Local convenience build:

```bash
export TAILWIND_BIN=/home/disane/.local/bin/tailwindcss
export TAILWIND_SHA256=73f0e5459054e5cfaa8ab6f3b940f3fbe0f13cc7fd83bc24e7c655033c203400
```

Build command once supplied:

```bash
scripts/build_tailwind.sh
```

The production Docker build does not use this local path. It fetches and verifies the pinned release asset in a build stage, then copies only the compiled CSS into the runtime image.
