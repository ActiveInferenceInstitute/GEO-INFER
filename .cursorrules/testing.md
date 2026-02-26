# Testing Requirements

## Core Principles

- Test all public methods and functions
- Use real data fixtures, never mock internal logic
- Test mathematical correctness of algorithms
- Achieve ≥80% coverage per module
- Run tests with `uv run pytest`

## Test Organisation

```
tests/
├── conftest.py          # Shared fixtures and test utilities
├── unit/                # Fast, isolated, no I/O
│   ├── test_core.py
│   └── test_utils.py
├── integration/         # Cross-module, may use I/O
│   └── test_pipeline.py
└── performance/         # Benchmarks, scalability
    └── test_benchmarks.py
```

### Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<method>_<scenario>_<expected>`
- Fixtures: descriptive nouns (`sample_geodata`, `risk_config`)

## Unit Testing

- Test all public methods with representative inputs
- Include edge cases: empty inputs, boundary values, None/NaN
- Test error paths: invalid inputs, missing data, type mismatches
- Verify mathematical correctness against known values
- Keep unit tests fast (< 1s each)

```python
import pytest
import numpy as np

def test_moran_i_positive_autocorrelation():
    """Clustered values should produce positive Moran's I."""
    coords = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    values = np.array([1.0, 1.0, 0.0, 0.0])
    result = compute_morans_i(coords, values)
    assert result > 0.0

def test_moran_i_insufficient_data():
    """< 3 points should return 0.0 gracefully."""
    result = compute_morans_i(np.array([[0, 0]]), np.array([1.0]))
    assert result == 0.0
```

## Integration Testing

- Test cross-module data flow
- Validate API endpoints with realistic payloads
- Test configuration loading from YAML
- Verify error propagation across module boundaries
- Test with real data samples (small fixtures checked into repo)

## Property-Based Testing

Use Hypothesis for algorithm correctness:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=1))
def test_normalise_preserves_length(values):
    """Normalisation should preserve list length."""
    result = normalise(values)
    assert len(result) == len(values)
```

Target ≥10 modules with property-based tests, prioritising:

- MATH (numerical operations)
- BAYES (probability distributions)
- SPACE (coordinate transformations)
- ACT (belief updates)

## Coverage Requirements

| Module Type | Minimum Coverage |
|------------|-----------------|
| Analytical Core (MATH, ACT, BAYES, AI) | 90% |
| Domain modules | 80% |
| Utility/Operations | 70% |

## Fixtures and Test Data

Use `conftest.py` for shared fixtures:

```python
import pytest

@pytest.fixture
def sample_geodata():
    """GeoJSON feature collection for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-122.4, 37.8]},
             "properties": {"value": 42.0}}
        ]
    }

@pytest.fixture
def risk_config():
    """Minimal risk engine configuration."""
    return {"hazard_types": ["earthquake", "flood"], "return_periods": [100, 250, 500]}
```

## Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--strict-markers -v"

[tool.coverage.run]
source = ["src/geo_infer_module"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Running Tests

```bash
# All tests
uv run pytest tests/

# Specific test file
uv run pytest tests/unit/test_core.py

# With coverage
uv run pytest tests/ --cov=src/geo_infer_module --cov-report=html

# Property-based tests only
uv run pytest tests/ -m hypothesis

# Performance benchmarks
uv run pytest tests/performance/ --benchmark-only
```

## CI Integration

Tests run automatically on every PR via GitHub Actions (`.github/workflows/ci.yml`). The CI pipeline:

1. Runs `uv run pytest` across all modules
2. Enforces coverage thresholds
3. Runs `ruff check` and `black --check`
4. Runs `mypy --strict` on core modules
