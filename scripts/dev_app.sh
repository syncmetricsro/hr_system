#!/usr/bin/env bash
#
# Run the full Jober web app locally for human testing / customer demos.
#
# Starts PostgreSQL + the production image in Docker, publishes the app on
# http://localhost:8000, runs migrations, and seeds fictional demo users.
#
# This is for local demos only: it serves the production image over plain HTTP,
# so it disables HTTPS redirect and secure cookies. NEVER use these flags on a
# real deployment.
#
# Usage:
#   scripts/dev_app.sh up        Build (if needed), start DB + app, migrate, seed.
#   scripts/dev_app.sh down      Stop and remove the app, DB, and network.
#   scripts/dev_app.sh status    Show container status and the URL.
#   scripts/dev_app.sh logs      Follow the app log.
#   scripts/dev_app.sh rebuild   Rebuild the image, then restart the app.
#
# Environment overrides: APP_IMAGE (default jober-platform:phase1), PORT (8000).
set -euo pipefail

IMAGE="${APP_IMAGE:-jober-platform:phase1}"
PORT="${PORT:-8000}"
NET=jober-dev-net
DB=jober-dev-db
APP=jober-dev-app
POSTGRES_IMAGE="postgres@sha256:2203e6282d9e7de7c24d7da234e2a744fb325df366a3fd8ed940e8abbee39527"

DB_ENV=(
  -e DB_NAME=jober -e DB_USER=jober -e DB_PASSWORD=jober-pass
  -e DB_HOST="$DB" -e DB_PORT=5432
)

build_image() {
  echo "Building $IMAGE ..."
  docker build -t "$IMAGE" .
}

ensure_image() {
  if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    build_image
  fi
}

wait_for_db() {
  for _ in $(seq 1 30); do
    docker exec "$DB" pg_isready -U jober -d jober >/dev/null 2>&1 && return 0
    sleep 1
  done
  echo "PostgreSQL did not become ready." >&2
  docker logs "$DB" >&2 || true
  exit 1
}

wait_for_app() {
  for _ in $(seq 1 30); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${PORT}/healthz/" || true)" = "200" ] && return 0
    sleep 1
  done
  echo "App did not become healthy." >&2
  docker logs "$APP" >&2 || true
  exit 1
}

manage() {
  docker run --rm --network "$NET" -e DJANGO_SECRET_KEY=dev-secret "${DB_ENV[@]}" "$IMAGE" python manage.py "$@"
}

print_access() {
  cat <<EOF

  Jober is running:  http://localhost:${PORT}

  Demo logins (password for all: demo-jober-2026):
    Manager/Admin   manazer@demo.jober.test
    Recruiter       naborar@demo.jober.test
    Coordinator     koordinator@demo.jober.test
    Observer        pozorovatel@demo.jober.test

  Stop with: scripts/dev_app.sh down
EOF
}

cmd_up() {
  ensure_image
  docker network inspect "$NET" >/dev/null 2>&1 || docker network create "$NET" >/dev/null

  if ! docker ps --format '{{.Names}}' | grep -q "^${DB}$"; then
    docker rm -f "$DB" >/dev/null 2>&1 || true
    echo "Starting PostgreSQL ..."
    docker run -d --name "$DB" --network "$NET" \
      -e POSTGRES_DB=jober -e POSTGRES_USER=jober -e POSTGRES_PASSWORD=jober-pass \
      "$POSTGRES_IMAGE" >/dev/null
    wait_for_db
  fi

  echo "Applying migrations ..."
  manage migrate --noinput >/dev/null
  echo "Seeding fictional demo users ..."
  manage seed_demo >/dev/null

  docker rm -f "$APP" >/dev/null 2>&1 || true
  echo "Starting app on port ${PORT} ..."
  docker run -d --name "$APP" --network "$NET" -p "${PORT}:8000" \
    -e DJANGO_SECRET_KEY=dev-secret \
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
  echo "Stopped and removed app, DB, and network."
}

cmd_status() {
  docker ps --filter "name=^${APP}$" --filter "name=^${DB}$" \
    --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
  echo "URL: http://localhost:${PORT}"
}

cmd_logs() { docker logs -f "$APP"; }

cmd_rebuild() { build_image; cmd_up; }

case "${1:-}" in
  up) cmd_up ;;
  down) cmd_down ;;
  status) cmd_status ;;
  logs) cmd_logs ;;
  rebuild) cmd_rebuild ;;
  *) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
