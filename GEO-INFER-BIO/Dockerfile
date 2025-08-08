# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy pyproject to leverage cache
COPY pyproject.toml ./

# Lock and sync dependencies
RUN uv lock && uv sync --no-dev

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/output

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports for API
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "src.geo_infer_bio.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]