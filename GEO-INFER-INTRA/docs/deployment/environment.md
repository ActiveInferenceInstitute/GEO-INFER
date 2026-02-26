# Environment Setup

This document covers Python environment configuration, package management, environment variables, configuration files, code quality tooling, and CI/CD setup for GEO-INFER.

## Python Requirements

GEO-INFER requires Python 3.9 or later. The framework uses `uv` as its package manager (not pip, conda, or poetry).

```bash
# Verify Python version
python3 --version  # Must be 3.9+

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify uv
uv --version
```

## Virtual Environment Setup

Create an isolated environment for GEO-INFER development:

```bash
# Navigate to the repository root
cd /path/to/GEO-INFER

# Create a virtual environment
uv venv

# Activate it (Linux/macOS)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate

# Install foundation modules
uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE ./GEO-INFER-ACT

# Install a module with development extras
uv pip install -e "./GEO-INFER-AI[dev,docs]"
```

Each module is installed in editable mode (`-e`) so that source changes take effect immediately without reinstallation.

## Module Installation

### Development Mode

```bash
# Single module
uv pip install -e ./GEO-INFER-MATH

# Multiple modules
uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE ./GEO-INFER-BAYES ./GEO-INFER-ACT

# All modules (for integration testing)
for dir in GEO-INFER-*/; do
    [ -f "$dir/pyproject.toml" ] && uv pip install -e "./$dir"
done
```

### Production Mode

In production, install without editable mode for smaller footprint:

```bash
uv pip install ./GEO-INFER-MATH ./GEO-INFER-SPACE ./GEO-INFER-ACT
```

## pyproject.toml Configuration

Each module has a `pyproject.toml` defining its metadata and dependencies. The root `pyproject.toml` configures shared tooling (Black, isort, mypy, flake8).

```toml
# Example: GEO-INFER-MATH/pyproject.toml
[project]
name = "geo-infer-math"
version = "0.2.0"
requires-python = ">=3.9"
dependencies = [
    "numpy>=1.24",
    "scipy>=1.10",
    "shapely>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "isort>=5.12",
    "mypy>=1.0",
    "flake8>=6.0",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
]
```

## Environment Variables

GEO-INFER uses environment variables for configuration that varies between environments (development, staging, production). Never hardcode credentials or connection strings.

### Core Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEO_INFER_ENV` | Deployment environment | `development`, `staging`, `production` |
| `GEO_INFER_LOG_LEVEL` | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `GEO_INFER_DATA_DIR` | Base path for local data storage | `/data/geo-infer` |
| `GEO_INFER_CACHE_DIR` | Cache directory for intermediate results | `/tmp/geo-infer-cache` |

### Database Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEO_INFER_DB_HOST` | PostgreSQL/PostGIS host | `localhost` |
| `GEO_INFER_DB_PORT` | PostgreSQL port | `5432` |
| `GEO_INFER_DB_NAME` | Database name | `geo_infer_db` |
| `GEO_INFER_DB_USER` | Database user | `geo_infer` |
| `GEO_INFER_DB_PASSWORD` | Database password | (set securely) |
| `GEO_INFER_REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

### External API Keys

| Variable | Description | Source |
|----------|-------------|--------|
| `NOAA_API_TOKEN` | NOAA Climate Data Online | ncdc.noaa.gov |
| `COPERNICUS_UID` | Copernicus CDS user ID | cds.climate.copernicus.eu |
| `COPERNICUS_API_KEY` | Copernicus CDS API key | cds.climate.copernicus.eu |
| `PLANET_API_KEY` | Planet Labs satellite imagery | planet.com |
| `MAPBOX_TOKEN` | Mapbox tile services | mapbox.com |
| `USGS_API_KEY` | USGS data services | usgs.gov |

### Cloud Storage Variables

| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_DEFAULT_REGION` | AWS region (e.g., `us-west-2`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob connection string |

## Configuration File Patterns

GEO-INFER supports three configuration patterns. Use the one that fits your deployment.

### YAML Configuration

```yaml
# config/geo_infer.yaml
environment: development

database:
  host: localhost
  port: 5432
  name: geo_infer_db
  pool_size: 5
  max_overflow: 10

spatial:
  default_crs: "EPSG:4326"
  h3_resolution: 7
  tile_cache_size_mb: 512

logging:
  level: INFO
  format: "%(asctime)s %(name)s %(levelname)s %(message)s"
```

Loading YAML configuration:

```python
from pathlib import Path
import yaml

def load_config(config_path: str = "config/geo_infer.yaml") -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path) as f:
        return yaml.safe_load(f)
```

### Environment File (.env)

```bash
# .env (git-ignored)
GEO_INFER_ENV=development
GEO_INFER_DB_HOST=localhost
GEO_INFER_DB_PORT=5432
GEO_INFER_DB_NAME=geo_infer_db
GEO_INFER_DB_USER=geo_infer
GEO_INFER_DB_PASSWORD=local_dev_password
GEO_INFER_REDIS_URL=redis://localhost:6379/0
NOAA_API_TOKEN=your_token_here
```

Loading with `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Reads .env file

db_host = os.environ.get("GEO_INFER_DB_HOST", "localhost")
db_port = int(os.environ.get("GEO_INFER_DB_PORT", "5432"))
```

### JSON Configuration

```json
{
  "environment": "production",
  "database": {
    "host": "db.internal",
    "port": 5432,
    "name": "geo_infer_db",
    "pool_size": 20
  },
  "spatial": {
    "default_crs": "EPSG:4326",
    "h3_resolution": 7
  }
}
```

## Secrets Management

### Development

Use `.env` files (excluded from git via `.gitignore`):

```bash
echo ".env" >> .gitignore
```

### Staging and Production

Use a secrets manager rather than environment files on disk.

**AWS Secrets Manager:**

```python
import boto3
import json

def get_secret(secret_name: str, region: str = "us-west-2") -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

db_creds = get_secret("geo-infer/database")
db_password = db_creds["password"]
```

**Kubernetes Secrets:**

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: geo-infer-secrets
type: Opaque
stringData:
  db-password: "production_password"
  redis-url: "redis://redis:6379/0"
  noaa-token: "production_noaa_token"
```

Mount into pods:

```yaml
env:
  - name: GEO_INFER_DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: geo-infer-secrets
        key: db-password
```

## Environment-Specific Configuration

### Development

```yaml
environment: development
database:
  host: localhost
  pool_size: 5
logging:
  level: DEBUG
spatial:
  tile_cache_size_mb: 256
```

### Staging

```yaml
environment: staging
database:
  host: staging-db.internal
  pool_size: 10
logging:
  level: INFO
spatial:
  tile_cache_size_mb: 1024
```

### Production

```yaml
environment: production
database:
  host: prod-db.internal
  pool_size: 30
  max_overflow: 20
logging:
  level: WARNING
spatial:
  tile_cache_size_mb: 4096
```

Select the configuration at startup:

```python
import os

env = os.environ.get("GEO_INFER_ENV", "development")
config = load_config(f"config/{env}.yaml")
```

## Code Quality Tools

All GEO-INFER modules share the same code quality configuration, defined in the root `pyproject.toml`.

### Black (Formatter)

Line length 88. Runs on all source files.

```bash
# Format a single module
black GEO-INFER-MATH/src/

# Check formatting without changing files
black --check GEO-INFER-MATH/src/

# Format the entire repo
black GEO-INFER-*/src/
```

### isort (Import Sorting)

Profile set to "black" for compatibility.

```bash
# Sort imports for a module
isort GEO-INFER-MATH/src/

# Check without modifying
isort --check-only GEO-INFER-MATH/src/
```

### mypy (Type Checking)

Strict mode enabled. All function parameters and return values require type annotations.

```bash
# Type-check a module
mypy GEO-INFER-MATH/src/

# Type-check with a specific config
mypy --config-file pyproject.toml GEO-INFER-MATH/src/
```

### flake8 (Linting)

```bash
# Lint a module
flake8 GEO-INFER-MATH/src/
```

### Running All Quality Checks

```bash
# Full quality sweep for a module
MODULE="GEO-INFER-MATH"
black --check "$MODULE/src/" && \
isort --check-only "$MODULE/src/" && \
mypy "$MODULE/src/" && \
flake8 "$MODULE/src/"
```

## CI/CD Environment Setup

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_USER: geo_infer
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: geo_infer_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Create virtual environment
        run: uv venv

      - name: Install modules
        run: |
          source .venv/bin/activate
          uv pip install -e ./GEO-INFER-MATH
          uv pip install -e ./GEO-INFER-SPACE
          uv pip install -e ./GEO-INFER-ACT
          uv pip install pytest pytest-cov

      - name: Run tests
        env:
          GEO_INFER_DB_HOST: localhost
          GEO_INFER_DB_PORT: 5432
          GEO_INFER_DB_NAME: geo_infer_test
          GEO_INFER_DB_USER: geo_infer
          GEO_INFER_DB_PASSWORD: test_password
        run: |
          source .venv/bin/activate
          uv run python GEO-INFER-TEST/run_unified_tests.py --category unit

      - name: Code quality
        run: |
          source .venv/bin/activate
          uv pip install black isort mypy flake8
          black --check GEO-INFER-MATH/src/
          isort --check-only GEO-INFER-MATH/src/
          flake8 GEO-INFER-MATH/src/
```

### Docker Development Environment

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app
COPY . .

RUN uv venv && \
    . .venv/bin/activate && \
    for dir in GEO-INFER-*/; do \
        [ -f "$dir/pyproject.toml" ] && uv pip install -e "./$dir"; \
    done

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "pytest", "GEO-INFER-TEST/"]
```

Build and run:

```bash
docker build -f Dockerfile.dev -t geo-infer-dev .
docker run --rm geo-infer-dev
```
