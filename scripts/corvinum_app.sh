#!/usr/bin/env bash
#
# Run the CorvinumEU PeopleOps thin client locally for demos (ADR 0022/0023).
#
# Same production image as Jober — DJANGO_SETTINGS_MODULE selects the client.
# Publishes http://localhost:8001 with its own PostgreSQL and network, so the
# Jober demo (scripts/dev_app.sh, port 8000) can run at the same time.
# Payslip emails go to the console backend: `scripts/corvinum_app.sh logs`
# shows the sent mail during the demo.
#
# Usage: scripts/corvinum_app.sh up|down|status|logs|rebuild
set -euo pipefail

IMAGE="${APP_IMAGE:-jober-platform:phase1}"
PORT="${PORT:-8001}"
NET=corvinum-dev-net
DB=corvinum-dev-db
APP=corvinum-dev-app
POSTGRES_IMAGE="postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527"

SETTINGS_ENV=(
  -e DJANGO_SETTINGS_MODULE=clients.corvinum_eu.production
  -e DJANGO_SECRET_KEY=dev-secret
  -e DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
)
DB_ENV=(
  -e DB_NAME=corvinum -e DB_USER=corvinum -e DB_PASSWORD=corvinum-pass
  -e DB_HOST="$DB" -e DB_PORT=5432
)

build_image() { echo "Building $IMAGE ..."; docker build -t "$IMAGE" .; }
ensure_image() { docker image inspect "$IMAGE" >/dev/null 2>&1 || build_image; }

wait_for_db() {
  for _ in $(seq 1 30); do
    docker exec "$DB" pg_isready -U corvinum -d corvinum >/dev/null 2>&1 && return 0
    sleep 1
  done
  echo "PostgreSQL did not become ready." >&2; docker logs "$DB" >&2 || true; exit 1
}

wait_for_app() {
  for _ in $(seq 1 30); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${PORT}/healthz/" || true)" = "200" ] && return 0
    sleep 1
  done
  echo "App did not become healthy." >&2; docker logs "$APP" >&2 || true; exit 1
}

manage() {
  docker run --rm --network "$NET" "${SETTINGS_ENV[@]}" "${DB_ENV[@]}" "$IMAGE" python manage.py "$@"
}

print_access() {
  cat <<EOF

  CorvinumEU PeopleOps is running:  http://localhost:${PORT}

  Demo logins (password for all: demo-corvinum-2026):
    HR Admin (manager)  hradmin@demo.corvinum.test   <- forced TOTP setup on first login
    Recruiter           recruiter@demo.corvinum.test
    Coordinator         coordinator@demo.corvinum.test
    Observer            observer@demo.corvinum.test

  Payslip emails print to the app log: scripts/corvinum_app.sh logs
  Stop with: scripts/corvinum_app.sh down
EOF
}

cmd_up() {
  ensure_image
  docker network inspect "$NET" >/dev/null 2>&1 || docker network create "$NET" >/dev/null
  if ! docker ps --format '{{.Names}}' | grep -q "^${DB}$"; then
    docker rm -f "$DB" >/dev/null 2>&1 || true
    echo "Starting PostgreSQL ..."
    docker run -d --name "$DB" --network "$NET" \
      -e POSTGRES_DB=corvinum -e POSTGRES_USER=corvinum -e POSTGRES_PASSWORD=corvinum-pass \
      "$POSTGRES_IMAGE" >/dev/null
    wait_for_db
  fi
  echo "Applying migrations ..."
  manage migrate --noinput >/dev/null
  echo "Seeding the fictional CorvinumEU scenario ..."
  manage seed_corvinum_demo >/dev/null
  docker rm -f "$APP" >/dev/null 2>&1 || true
  echo "Starting app on port ${PORT} ..."
  docker run -d --name "$APP" --network "$NET" -p "${PORT}:8000" \
    "${SETTINGS_ENV[@]}" \
    -e DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,${APP}" \
    -e DJANGO_SECURE_SSL_REDIRECT=0 \
    -e DJANGO_SESSION_COOKIE_SECURE=0 \
    -e DJANGO_CSRF_COOKIE_SECURE=0 \
    "${DB_ENV[@]}" "$IMAGE" >/dev/null
  wait_for_app
  print_access
}

cmd_down() {
  docker rm -f "$APP" >/dev/null 2>&1 || true
  docker rm -f "$DB" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
  echo "Stopped and removed the CorvinumEU app, DB, and network."
}

case "${1:-}" in
  up) cmd_up ;;
  down) cmd_down ;;
  rebuild) build_image; cmd_up ;;
  status)
    docker ps --filter "name=${APP}" --filter "name=${DB}" --format 'table {{.Names}}\t{{.Status}}'
    echo "URL: http://localhost:${PORT}"
    ;;
  logs) docker logs -f "$APP" ;;
  *) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
