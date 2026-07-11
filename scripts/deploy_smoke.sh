#!/usr/bin/env bash
#
# Post-deploy smoke check (deployment-plan.md "release step"). Run against any
# app instance — local demo or a Dokku app — right after deploy/migrate:
#
#   scripts/deploy_smoke.sh http://localhost:8000
#   scripts/deploy_smoke.sh https://staging.example.com --https
#
# Checks (curl + grep only, no dependencies):
#   1. /healthz/ answers "ok"
#   2. the login page renders (HTTP 200, CSRF token present)
#   3. static files serve fingerprinted with a long-lived cache header
#   4. security headers: X-Frame-Options everywhere; with --https also HSTS,
#      and the session cookie must be Secure
# Exits non-zero on the first failure — wire it into the deploy pipeline.
set -euo pipefail

BASE="${1:?usage: deploy_smoke.sh <base-url> [--https]}"
BASE="${BASE%/}"
HTTPS_MODE="${2:-}"

fail() { echo "FAIL: $*" >&2; exit 1; }
note() { echo "  ok: $*"; }

echo "Deploy smoke against $BASE"

# 1. healthz
body="$(curl -fsS --max-time 10 "$BASE/healthz/")" || fail "/healthz/ unreachable"
[ "$body" = "ok" ] || fail "/healthz/ returned '$body' (expected 'ok')"
note "healthz"

# 2. login page + CSRF (follow the language redirect)
login="$(curl -fsSL --max-time 10 -c /dev/null "$BASE/")" || fail "root/login page unreachable"
echo "$login" | grep -q "csrfmiddlewaretoken" || fail "login page carries no CSRF token"
note "login page + CSRF"

# 3. fingerprinted static with immutable caching
css_path="$(echo "$login" | grep -o 'href="[^"]*dist/css/app\.[a-f0-9]*\.css"' | head -1 | cut -d'"' -f2)"
[ -n "$css_path" ] || fail "no fingerprinted app.css referenced on the page (collectstatic/manifest problem)"
headers="$(curl -fsSI --max-time 10 "$BASE$css_path")" || fail "static file $css_path unreachable"
echo "$headers" | grep -qi "content-type: text/css" || fail "static served with wrong content type"
echo "$headers" | grep -qi "cache-control: .*immutable" || fail "static served without immutable cache header"
note "static ($css_path)"

# 4. security headers
page_headers="$(curl -fsS --max-time 10 -L -o /dev/null -D - "$BASE/")"
echo "$page_headers" | grep -qi "x-frame-options" || fail "missing X-Frame-Options"
note "X-Frame-Options"
if [ "$HTTPS_MODE" = "--https" ]; then
  echo "$page_headers" | grep -qi "strict-transport-security" || fail "missing HSTS on HTTPS deployment"
  note "HSTS"
  cookie_headers="$(curl -fsS --max-time 10 -o /dev/null -D - "$BASE/" | grep -i 'set-cookie' || true)"
  if [ -n "$cookie_headers" ]; then
    echo "$cookie_headers" | grep -qi "secure" || fail "cookies set without Secure on HTTPS deployment"
    note "Secure cookies"
  fi
fi

echo "Deploy smoke PASSED for $BASE"
