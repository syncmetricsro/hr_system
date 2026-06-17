#!/usr/bin/env bash
set -euo pipefail

image="${1:-jober-platform:phase0}"

docker run --rm "$image" sh -eu -c '
  for binary in node npm pnpm yarn tailwindcss chromium chromium-browser google-chrome chrome firefox webkit playwright; do
    if command -v "$binary" >/dev/null 2>&1; then
      echo "Forbidden binary present in runtime image: $binary" >&2
      exit 1
    fi
  done

  forbidden_files="$(find /app /ms-playwright /root/.cache/ms-playwright /home \
    \( -name package.json \
       -o -name package-lock.json \
       -o -name pnpm-lock.yaml \
       -o -name pnpm-workspace.yaml \
       -o -name yarn.lock \
       -o -name npm-shrinkwrap.json \
       -o -name "vite.config.*" \
       -o \( -name "tailwindcss*" ! -name "*.sha256" \) \
       -o -name "chrome" \
       -o -name "chromium" \
       -o -name "chromium-browser" \
       -o -name "firefox" \
       -o -name "webkit" \
       -o -name "ms-playwright" \
       -o -name "*playwright*" \
    \) -print 2>/dev/null || true)"

  if [ -n "$forbidden_files" ]; then
    echo "Forbidden files present in runtime image:" >&2
    echo "$forbidden_files" >&2
    exit 1
  fi

  if [ -d /ms-playwright ] || [ -d /root/.cache/ms-playwright ]; then
    echo "Forbidden Playwright browser directory present in runtime image" >&2
    exit 1
  fi

  test -d /app

  test -f /app/static/dist/css/app.css
  test -f /app/staticfiles/dist/css/app.css
  if python - <<PY
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("playwright") is None else 1)
PY
  then
    :
  else
    echo "Forbidden Python Playwright package present in runtime image" >&2
    exit 1
  fi
'

if docker history --no-trunc "$image" | grep -iE 'mcr.microsoft.com/playwright|ms-playwright|playwright/python' >/dev/null; then
  echo "Forbidden Playwright reference found in production image history" >&2
  exit 1
fi

echo "Production image runtime artifact check passed for $image."
