# filename: docker-entrypoint-init.sh
#!/usr/bin/env bash
set -euo pipefail

# Wait for possible dependent services; for SQLite this is instant.
# For Postgres/MySQL metadata DB, add waits here.

# Initialize database and create admin user if not exists
superset db upgrade

# Create admin user from env vars
# SUPERSET_ADMIN_USERNAME, SUPERSET_ADMIN_PASSWORD, SUPERSET_ADMIN_EMAIL
if [ -n "${SUPERSET_ADMIN_USERNAME:-}" ] && [ -n "${SUPERSET_ADMIN_PASSWORD:-}" ]; then
  superset fab create-admin \
    --username "${SUPERSET_ADMIN_USERNAME}" \
    --firstname Admin \
    --lastname User \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@superset.local}" \
    --password "${SUPERSET_ADMIN_PASSWORD}"
fi

# Load default roles and examples disabled by default
# superset load_examples

# Setup roles and init
superset init

# Start the webserver
gunicorn \
  -w ${SUPERSET_GUNICORN_WORKERS:-4} \
  -k gevent \
  --timeout ${SUPERSET_GUNICORN_TIMEOUT:-120} \
  -b 0.0.0.0:8088 \
  "superset.app:create_app()"

