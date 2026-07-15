#!/usr/bin/env bash
# Start Corvinum staging only for rehearsals, deploy checks, and restore drills.
# It is deliberately not a permanent service on the cost-first 4 GB host.
set -euo pipefail

action="${1:-status}"
app="${DOKKU_STAGING_APP:-corvinum-staging}"

command -v dokku >/dev/null 2>&1 || { echo "dokku is required on the deployment host" >&2; exit 1; }
case "$action" in
  start)
    dokku ps:start "$app"
    echo "${app} started. Run its smoke checks, then stop it when the rehearsal is complete."
    ;;
  stop)
    dokku ps:stop "$app"
    echo "${app} stopped."
    ;;
  status)
    dokku ps:report "$app"
    ;;
  *)
    echo "Usage: $0 {start|stop|status}" >&2
    exit 64
    ;;
esac
