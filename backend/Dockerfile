# ================================
# Stage 1: Builder
# ================================
FROM python:3.12-alpine AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=2.3.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Add poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install build dependencies (only needed for compilation)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Set work directory
WORKDIR /app

# Copy Poetry files (including lock file for deterministic builds)
COPY pyproject.toml poetry.lock ./

# Install dependencies (production only)
RUN poetry install --no-root --only main

# ================================
# Stage 2: Runtime
# ================================
FROM python:3.12-alpine AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install only runtime dependencies (no build tools)
RUN apk add --no-cache \
    libpq \
    postgresql-client \
    curl

# Create non-root user
RUN adduser -D -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set work directory
WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/celery /usr/local/bin/celery

# Copy application code
COPY --chown=appuser:appuser . .

# Copy and set entrypoint script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
