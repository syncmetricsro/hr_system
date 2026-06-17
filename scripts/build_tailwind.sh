#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${TAILWIND_BIN:-}" ]]; then
  echo "TAILWIND_BIN must point to the human-supplied Tailwind v4.3.0 binary." >&2
  exit 1
fi

TAILWIND_SHA256="${TAILWIND_SHA256:-$(awk '{print $1}' vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256)}"

actual_sha="$(sha256sum "$TAILWIND_BIN" | awk '{print $1}')"
if [[ "$actual_sha" != "$TAILWIND_SHA256" ]]; then
  echo "Tailwind checksum mismatch." >&2
  echo "Expected: $TAILWIND_SHA256" >&2
  echo "Actual:   $actual_sha" >&2
  exit 1
fi

"$TAILWIND_BIN" \
  -i static/src/css/app.css \
  -o static/dist/css/app.css \
  --minify
