# GEO-INFER-BIO/tests

Tests workspace within `GEO-INFER-BIO`.

## Contents

- `integration/`
- `unit/`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-BIO`
- Package: `geo_infer_bio`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-BIO`
- Tests: `uv run python -m pytest GEO-INFER-BIO/tests`

## Dependencies

- `numpy>=1.21.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `biopython>=1.79`
- `networkx>=2.6.0`
- `scikit-learn>=0.24.0`
- `matplotlib>=3.4.0`
- `seaborn>=0.11.0`
- `geopandas>=0.9.0`
- `shapely>=1.8.0`
- `fastapi>=0.68.0`
- `uvicorn>=0.15.0`


## Strict Test Inventory

- Purpose: validate the `GEO-INFER-BIO` module's current behavior through unit,
  integration, system, and performance test surfaces.
- Primary marker: tests receive exactly one primary marker from their canonical
  directory; additive domain markers remain allowed.
- Required fixtures: local `tests/conftest.py` fixtures and shared
  `geo_infer_test.testing` fixtures for deterministic RNG, filesystem, HTTP,
  SQLite, service, model, and artifact boundaries.
- Dependencies: required test/runtime dependencies are installed by
  `uv sync --all-packages --all-extras`; missing backends are failures.
- Expected artifacts: JUnit XML under `.geo-infer-test-results/`; model and
  visualization outputs require finite statistics, sidecars, hashes, and a
  manifest.
- Failure triage: `env -u VIRTUAL_ENV uv run pytest -c pyproject.toml -q
  GEO-INFER-BIO/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.

## Validation

```bash
uv run python -m pytest GEO-INFER-BIO/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
