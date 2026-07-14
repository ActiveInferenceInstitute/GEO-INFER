# GEO-INFER-EXAMPLES/examples/health_integration/disease_surveillance_pipeline/scripts

Scripts workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `run_surveillance_pipeline.py`

## Public Interface

- `run_surveillance_pipeline.py:setup_logging` (function)
- `run_surveillance_pipeline.py:DiseaseSurveillancePipeline` (class)
- `run_surveillance_pipeline.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-EXAMPLES`
- Package: `geo_infer_examples`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EXAMPLES`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module EXAMPLES`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --module EXAMPLES
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
