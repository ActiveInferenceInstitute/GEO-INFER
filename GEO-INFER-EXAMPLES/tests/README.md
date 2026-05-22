# GEO-INFER-EXAMPLES/tests

Tests workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_examples_module.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-EXAMPLES`
- Package: `geo_infer_examples`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EXAMPLES`
- Tests: `uv run python -m pytest GEO-INFER-EXAMPLES/tests`

## Dependencies

- `jupyterlab>=3.4.0`
- `matplotlib>=3.5.0`
- `pandas>=1.4.0`
- `pyyaml>=6.0`
- `requests>=2.28.0`
- `rich>=12.0.0`
- `typer>=0.7.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-EXAMPLES/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
