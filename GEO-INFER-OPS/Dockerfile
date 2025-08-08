# Build stage
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./

# Lock and sync dependencies
RUN uv lock && uv sync --no-dev --no-install-project

# Copy source code
COPY src/ src/

# Final stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GEO_INFER_OPS_CONFIG="/app/config/local.yaml" \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src"

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy uv virtual environment
COPY --from=builder /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/config /app/logs \
    && chown -R appuser:appuser /app

# Copy application code
COPY --from=builder /app/src /app/src
COPY config /app/config

# Set ownership and permissions
RUN chown -R appuser:appuser /app \
    && chmod -R 755 /app \
    && chmod -R 777 /app/logs

# Switch to non-root user
USER appuser

# Create volume for configuration and logs
VOLUME ["/app/config", "/app/logs"]

# Expose ports
EXPOSE 8000
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "geo_infer_ops.app"] 