# Multi-stage Dockerfile for GEO-INFER-IOT
# Build stage
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libpq-dev \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY ../setup.py ../requirements.txt* ../pyproject.toml* ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir gunicorn uvicorn[standard]

# Production stage
FROM python:3.11-slim as production

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r geo_infer && useradd -r -g geo_infer geo_infer

# Set work directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ../src /app/src
COPY ../config /app/config
COPY ../deployment/docker-entrypoint.sh /usr/local/bin/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config && \
    chown -R geo_infer:geo_infer /app

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    CONFIG_PATH=/app/config/iot_config.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER geo_infer

# Expose ports
EXPOSE 8000 8001

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command
CMD ["uvicorn", "geo_infer_iot.api.sensor_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
