#!/bin/bash
set -e

# Wait for postgres
echo "Waiting for postgres..."
MAX_RETRIES=30
RETRY_COUNT=0

while ! pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-noteapp_user}" -d "${DB_NAME:-noteapp_db}"; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERROR: PostgreSQL did not become ready in time"
    exit 1
  fi
  echo "Waiting for PostgreSQL... (attempt $RETRY_COUNT/$MAX_RETRIES)"
  sleep 1
done
echo "PostgreSQL is ready!"

# Run migrations (skip if SKIP_MIGRATIONS is set)
if [ "$SKIP_MIGRATIONS" != "true" ]; then
  echo "Running database migrations..."
  
  # Retry logic for migrations (database might still be initializing)
  MAX_MIGRATION_RETRIES=5
  MIGRATION_RETRY_COUNT=0
  
  while [ $MIGRATION_RETRY_COUNT -lt $MAX_MIGRATION_RETRIES ]; do
    if python manage.py migrate --noinput; then
      echo "Migrations completed successfully!"
      break
    else
      MIGRATION_RETRY_COUNT=$((MIGRATION_RETRY_COUNT + 1))
      if [ $MIGRATION_RETRY_COUNT -ge $MAX_MIGRATION_RETRIES ]; then
        echo "ERROR: Migrations failed after $MAX_MIGRATION_RETRIES attempts"
        exit 1
      fi
      echo "Migration attempt $MIGRATION_RETRY_COUNT failed, retrying in 2 seconds..."
      sleep 2
    fi
  done
else
  echo "Skipping migrations (SKIP_MIGRATIONS=true)"
fi

# Create superuser if it doesn't exist (optional, for development)
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser \
        --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

# Collect static files (if needed in production)
# python manage.py collectstatic --noinput

# If arguments are provided, execute them (for celery worker, etc.)
# Otherwise, start Gunicorn (for API service)
if [ "$#" -gt 0 ]; then
  echo "Executing command: $@"
  exec "$@"
else
  # Start Gunicorn with configurable workers
  WORKERS=${GUNICORN_WORKERS:-4}
  THREADS=${GUNICORN_THREADS:-2}
  
  echo "Starting Gunicorn with $WORKERS workers and $THREADS threads per worker..."
  exec gunicorn api.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers "$WORKERS" \
      --threads "$THREADS" \
      --access-logfile - \
      --error-logfile - \
      --log-level info
fi
