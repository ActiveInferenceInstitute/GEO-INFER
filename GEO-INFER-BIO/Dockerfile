# Use Python 3.12 slim image (matches requires-python >=3.11)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy pyproject to leverage cache
COPY pyproject.toml ./

# The `geo-infer` cross-member extra maps to uv workspace members that do not
# exist in the standalone image context; strip it and its workspace sources so
# the base-runtime lock resolves (verified: resolves 114 packages).
RUN sed -i '/^geo-infer = \[$/,/^\]$/d; /^\[tool\.uv\.sources\]/,$d' pyproject.toml \
    && uv lock && uv sync --no-dev --no-install-project

# Copy the rest of the application
COPY . .

# Install the project distribution itself (now that src/ is present)
RUN uv sync --no-dev

# Create necessary directories
RUN mkdir -p /app/data /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose ports for API
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "geo_infer_bio.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]