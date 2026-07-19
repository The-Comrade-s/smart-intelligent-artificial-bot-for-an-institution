# syntax=docker/dockerfile:1

# --- Build stage: install dependencies into a venv for a smaller final image ---
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

# Railway injects the PORT environment variable at runtime (defaults to
# 8000 if unset). Railway's platform-level health check is configured
# separately (see backend/railway.json and docs/DEPLOYMENT.md) against
# the same /api/v1/health path — this Docker-level HEALTHCHECK is a
# secondary safety net, useful for local `docker run` testing too.
ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f "http://localhost:${PORT}/api/v1/health" || exit 1

# Shell form so ${PORT} expands at container start (Railway sets this dynamically).
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
