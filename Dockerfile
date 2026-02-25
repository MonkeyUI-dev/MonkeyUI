# syntax = docker/dockerfile:1

# -----------------------------------------------------------------------------
# Stage 1: Build React Frontend (Vite)
# -----------------------------------------------------------------------------
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install

COPY frontend/ ./
ENV VITE_API_URL=/api
RUN npm run build


# -----------------------------------------------------------------------------
# Stage 2: Build Python venv with uv (deps + project)
# -----------------------------------------------------------------------------
FROM python:3.14-slim AS backend-builder
WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Cacheable deps layer (MUST include uv.lock for --frozen)
COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy source + install project
COPY backend/ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable


# -----------------------------------------------------------------------------
# Stage 3: Production runtime image
# -----------------------------------------------------------------------------
FROM python:3.14-slim AS production
WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd --create-home --shell /bin/bash appuser

# Copy venv + app
COPY --from=backend-builder /opt/venv /opt/venv
COPY --from=backend-builder /app/backend /app/backend

# Copy frontend build output into Django staticfiles
COPY --from=frontend-builder /app/frontend/dist /app/backend/staticfiles/frontend

RUN mkdir -p /app/backend/media /app/backend/staticfiles \
 && chown -R appuser:appuser /app/backend

USER appuser

RUN /opt/venv/bin/python manage.py collectstatic --noinput

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/health/ || exit 1

# Default command
# For local development/testing only
CMD /opt/venv/bin/python manage.py migrate --noinput && \
    /opt/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile -