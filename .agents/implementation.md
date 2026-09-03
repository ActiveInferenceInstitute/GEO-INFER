# Implementation Guidelines

## Code Quality Standards

- Use professional, functional, modular, concise code
- Follow PEP 8 with Black formatting and isort import ordering
- Apply ruff for linting (`ruff check --fix`)
- Use type hints for all function parameters and return values
- Write clearly-commented, interpretable code
- Implement proper error handling and structured logging

## Logging

Every module must use structured logging via the standard library:

```python
import logging
logger = logging.getLogger(__name__)

class Engine:
    def process(self, data: list[dict]) -> dict:
        logger.info("Starting processing, records=%d", len(data))
        try:
            result = self._compute(data)
            logger.debug("Computation complete, keys=%s", list(result.keys()))
            return result
        except ValueError as e:
            logger.error("Validation failed: %s", e)
            raise
```

**Rules**:

- `DEBUG`: Internal state, intermediate values
- `INFO`: Normal operations (start/stop, record counts)
- `WARNING`: Degraded operation (missing optional deps, fallback behaviour)
- `ERROR`: Failures that affect output
- Never use `print()` in library code

## Dependency Management

- Use `uv` for all package operations (`uv pip install`, `uv run python`)
- Declare dependencies in `pyproject.toml` under `[project.dependencies]`
- Use optional dependency groups for heavy/specialised packages:

```toml
[project.optional-dependencies]
spatial = ["geopandas>=0.14", "h3>=4.5.0,<5"]
bayesian = ["pymc>=5.0", "arviz>=0.17"]
```

- Use lazy imports with fallback for optional dependencies:

```python
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    logger.warning("geopandas not available; spatial features disabled")
```

## Configuration

- Store configuration in YAML files under `config/`
- Load with `yaml.safe_load()`, never `yaml.load()`
- Validate against JSON Schema where applicable
- Use environment variables for secrets: `os.environ.get("API_KEY")`
- Never hardcode credentials, URLs, or environment-specific values

```python
import os
import yaml

def load_config(path: str = "config/default.yaml") -> dict:
    with open(path) as f:
        config = yaml.safe_load(f)
    # Override with environment variables
    config["api_key"] = os.environ.get("GEO_INFER_API_KEY", config.get("api_key", ""))
    return config
```

## Mathematical Rigor

- Ground implementations in solid mathematical foundations
- Use numpy/scipy for numerical computations
- Implement proper statistical methods for uncertainty
- Validate mathematical correctness with unit tests
- Document mathematical assumptions and limitations in docstrings
- Include mathematical derivations and citations

## Geospatial Standards

- Use established libraries: geopandas, shapely, rasterio, h3 (v4 only)
- Implement proper CRS handling (always specify EPSG codes)
- Support standard formats: GeoJSON, Shapefile, GeoTIFF, COG
- Follow OGC standards where applicable
- Use H3 v4 API exclusively:
  - `h3.latlng_to_cell()` (not `h3.geo_to_h3()`)
  - `h3.cell_to_latlng()` (not `h3.h3_to_geo()`)
  - `h3.grid_disk()` (not `h3.k_ring()`)

## Async Patterns

For I/O-bound operations and API endpoints, use `asyncio`:

```python
import asyncio
from typing import Any

async def fetch_data(source_id: str) -> dict[str, Any]:
    """Fetch data from an external source asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/data/{source_id}") as resp:
            resp.raise_for_status()
            return await resp.json()
```

- Use `async def` for I/O-bound methods
- Use `asyncio.gather()` for concurrent operations
- Use `asyncio.Queue` for producer-consumer patterns
- Always handle `asyncio.CancelledError` in long-running tasks
- FastAPI endpoints should be `async def` when performing I/O

## Type Safety

- Use type hints everywhere: parameters, returns, class attributes
- Run `mypy --strict` on analytical core modules (MATH, ACT, BAYES)
- Use `TypeVar`, `Generic`, `Protocol` for complex type relationships
- Use runtime validation with Pydantic models for API boundaries

```python
from typing import Optional
from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Optional[dict[str, str]] = None
```

## Error Handling

- Always catch specific exceptions, never bare `except:`
- Provide context in error messages
- Use custom exception classes for domain-specific errors
- Log errors before re-raising when appropriate
- Implement retry logic for transient failures (network, I/O)

```python
class GeoInferError(Exception):
    """Base exception for GEO-INFER modules."""

class DataValidationError(GeoInferError):
    """Raised when input data fails validation."""

class IntegrationError(GeoInferError):
    """Raised when cross-module communication fails."""
```
