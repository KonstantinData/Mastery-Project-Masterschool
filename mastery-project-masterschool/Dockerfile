# syntax=docker/dockerfile:1

## Base image
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

## Create non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

## Copy project files
COPY . /app

## Install Python dependencies
RUN pip install --no-cache-dir pip && \
    pip install --no-cache-dir .

## Drop privileges
USER appuser

## Healthcheck to verify CLI executes without error
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD travel_perks execute --dry-run || exit 1

## Default command
CMD ["travel_perks", "execute"]