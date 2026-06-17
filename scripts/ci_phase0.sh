#!/usr/bin/env bash
set -euo pipefail

image="${IMAGE:-jober-platform:phase0}"

python3 scripts/check_no_node_artifacts.py
python3 scripts/verify_vendor_assets.py
python3 -m py_compile \
  manage.py \
  config/asgi.py \
  config/wsgi.py \
  config/urls.py \
  config/settings/base.py \
  config/settings/local.py \
  config/settings/production.py \
  apps/core/apps.py \
  apps/core/views.py \
  scripts/check_no_node_artifacts.py \
  scripts/fetch_tailwind.py \
  scripts/verify_vendor_assets.py \
  scripts/write_requirements_lock.py

docker build --no-cache -t "$image" .
scripts/check_production_image.sh "$image"
scripts/playwright_smoke.sh
