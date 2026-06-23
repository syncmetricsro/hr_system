#!/usr/bin/env bash
#
# Extract and compile translation catalogs (locale/<lang>/LC_MESSAGES/django.{po,mo}).
#
# gettext (xgettext/msgfmt) is not in the runtime/test images, so this runs the
# app image with gettext apt-installed at build/run time. .po is the source of
# truth (committed and hand-edited); .mo is the compiled artifact the app loads.
#
# Usage:
#   scripts/compile_messages.sh            Compile existing .po -> .mo.
#   scripts/compile_messages.sh --extract  Re-extract msgids from source first
#                                          (updates .po), then compile.
set -euo pipefail

IMAGE="${APP_IMAGE:-jober-platform:phase1}"
LANGS=(sk hu uk)
UID_GID="$(id -u):$(id -g)"

extract=""
[ "${1:-}" = "--extract" ] && extract="yes"

lang_args=""
for l in "${LANGS[@]}"; do lang_args="$lang_args -l $l"; done

docker run --rm -u 0 \
  -e DJANGO_SETTINGS_MODULE=config.settings.local -e DJANGO_SECRET_KEY=x -e HOME=/tmp \
  -v "$PWD:/app" -w /app \
  "$IMAGE" bash -c "
    set -e
    apt-get update -qq && apt-get install -y -qq gettext >/dev/null 2>&1
    ${extract:+python manage.py makemessages $lang_args -i demo -i test-artifacts -i vendor -i staticfiles}
    python manage.py compilemessages $lang_args
    chown -R $UID_GID locale
  "
echo "Done. Catalogs in locale/<lang>/LC_MESSAGES/"
