#!/usr/bin/env bash
#
# Safely extract, validate, and compile locale/<lang>/LC_MESSAGES/django.{po,mo}.
#
# Usage:
#   scripts/compile_messages.sh
#       Validate every active translation and deterministically compile .mo files.
#   scripts/compile_messages.sh --check
#       Validate catalogs and confirm committed .mo files are current; write nothing.
#   scripts/compile_messages.sh --extract
#       Extract source msgids without compiling. Refuses active -> obsolete changes.
#   scripts/compile_messages.sh --extract --accept-obsolete
#       Extract after explicitly approving the reported active -> obsolete changes.
set -euo pipefail

IMAGE="$(printenv APP_IMAGE || true)"
if [[ -z "$IMAGE" ]]; then
  IMAGE="jober-platform:phase1"
fi
UID_GID="$(id -u):$(id -g)"

usage() {
  sed -n '3,14p' "$0" >&2
}

run_compiler() {
  docker run --rm \
    --user "$UID_GID" \
    -e HOME=/tmp \
    -v "$PWD:/app" \
    -w /app \
    "$IMAGE" \
    python scripts/compile_po.py "$@" \
    locale/sk/LC_MESSAGES/django.po \
    locale/hu/LC_MESSAGES/django.po \
    locale/uk/LC_MESSAGES/django.po
}

mode="compile"
accept_obsolete="no"
if (($#)); then
  case "$1" in
    --check)
      (($# == 1)) || { usage; exit 2; }
      mode="check"
      ;;
    --extract)
      mode="extract"
      shift
      if (($#)); then
        [[ "$1" == "--accept-obsolete" && $# == 1 ]] || { usage; exit 2; }
        accept_obsolete="yes"
      fi
      ;;
    *)
      usage
      exit 2
      ;;
  esac
fi

if [[ "$mode" == "compile" ]]; then
  run_compiler
  echo "Compiled validated catalogs in locale/<lang>/LC_MESSAGES/."
  exit 0
fi

if [[ "$mode" == "check" ]]; then
  run_compiler --check
  exit 0
fi

snapshot_dir="$(mktemp -d /tmp/jober-i18n.XXXXXX)"
restore_pending="yes"
cleanup() {
  if [[ "$restore_pending" == "yes" ]]; then
    python3 scripts/i18n_catalog.py restore \
      --source "$snapshot_dir" \
      --destination locale
  fi
  rm -rf -- "$snapshot_dir"
}
trap cleanup EXIT

python3 scripts/i18n_catalog.py snapshot \
  --source locale \
  --destination "$snapshot_dir"

docker run --rm -u 0 \
  -e DJANGO_SETTINGS_MODULE=config.settings.local \
  -e DJANGO_SECRET_KEY=x \
  -e HOME=/tmp \
  -v "$PWD:/app" \
  -w /app \
  "$IMAGE" \
  bash -c "
    set -euo pipefail
    return_locale_ownership() {
      chown -R $UID_GID locale
    }
    trap return_locale_ownership EXIT
    apt-get update -qq
    apt-get install -y -qq gettext >/dev/null 2>&1
    python manage.py safe_makemessages \
      -l sk -l hu -l uk \
      -i tests -i demo -i test-artifacts -i vendor -i staticfiles
  "

python3 scripts/i18n_catalog.py preserve-metadata \
  --source "$snapshot_dir" \
  --destination locale

if [[ "$accept_obsolete" == "yes" ]]; then
  python3 scripts/i18n_catalog.py report \
    --before "$snapshot_dir" \
    --after locale \
    --accept-obsolete
else
  python3 scripts/i18n_catalog.py report \
    --before "$snapshot_dir" \
    --after locale
fi

restore_pending="no"
echo "Extraction complete; catalogs were not compiled."
echo "Translate every added msgid, then run scripts/compile_messages.sh."
