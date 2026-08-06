#!/usr/bin/env bash
# Capture Help-area screenshots from the seeded demo stacks.
#
# Reuses the browser harness that already builds both apps, seeds both
# databases and drives Chromium, so regenerating the Help imagery is one
# command rather than a manual ritual. A screenshot that lies is worse than no
# screenshot: re-run this whenever the shell or a captured page changes.
#
# Fictional seed data only, by construction - the harness seeds demo.jober.test
# and demo.corvinum.test and never touches a real-data environment.
set -euo pipefail

cd "$(dirname "$0")/.."

export E2E_PYTEST_ARGS="tests/e2e/capture_help_screens.py"
export HELP_SCREENS_DIR="${HELP_SCREENS_DIR:-/app/static/help/screens}"

if [[ -n "${HELP_CAPTURE_SLUGS:-}" ]]; then
  echo "Capturing selected Help screenshots (${HELP_CAPTURE_SLUGS}) from fictional seeds ..."
else
  echo "Capturing Jober SK and Corvinum HU Help screenshots from fictional seeds ..."
fi
scripts/playwright_e2e.sh "$@"

echo
echo "Captured:"
find static/help/screens -type f -name '*.webp' | sort
echo
echo "Review these before committing - a screenshot that lies is worse than none."
