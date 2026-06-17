FROM python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9 AS tailwind

WORKDIR /app

ARG TAILWIND_VERSION=4.3.0
ARG TAILWIND_ASSET=tailwindcss-linux-x64

COPY scripts/fetch_tailwind.py /app/scripts/fetch_tailwind.py
COPY vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256 /app/vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256
COPY static/src/css/app.css /app/static/src/css/app.css

RUN python scripts/fetch_tailwind.py \
    --version "$TAILWIND_VERSION" \
    --asset "$TAILWIND_ASSET" \
    --expected-sha-file /app/vendor/tailwind/tailwindcss-v4.3.0-linux-x64.sha256 \
    --output /tmp/tailwindcss \
    && mkdir -p /app/static/dist/css \
    && /tmp/tailwindcss \
       -i /app/static/src/css/app.css \
       -o /app/static/dist/css/app.css \
       --minify \
    && rm -f /tmp/tailwindcss /tmp/tailwindcss.sha256sums.txt

FROM python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9 AS wheels

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements/runtime.lock /app/requirements/runtime.lock

RUN python -m pip download \
    --require-hashes \
    --only-binary=:all: \
    --dest /wheels \
    -r requirements/runtime.lock

FROM python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9 AS runtime

ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN addgroup --system jober && adduser --system --ingroup jober --home /app jober

COPY --from=wheels /wheels /wheels
COPY requirements/runtime.lock /app/requirements/runtime.lock

RUN python -m pip install \
    --no-cache-dir \
    --no-index \
    --find-links=/wheels \
    --require-hashes \
    -r requirements/runtime.lock \
    && rm -rf /wheels

COPY manage.py /app/manage.py
COPY apps /app/apps
COPY config /app/config
COPY templates /app/templates
COPY static/vendor /app/static/vendor
COPY static/src/js /app/static/src/js
COPY --from=tailwind /app/static/dist/css/app.css /app/static/dist/css/app.css

RUN test -f static/dist/css/app.css \
    && DJANGO_SECRET_KEY=build-only-secret \
       DJANGO_ALLOWED_HOSTS=localhost \
       DB_NAME=jober \
       DB_USER=jober \
       DB_PASSWORD=unused \
       DB_HOST=localhost \
       python manage.py collectstatic --noinput \
    && chown -R jober:jober /app

USER jober

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
