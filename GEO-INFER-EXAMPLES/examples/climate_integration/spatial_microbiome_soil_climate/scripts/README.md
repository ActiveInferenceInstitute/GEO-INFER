# GEO-INFER-EXAMPLES/examples/climate_integration/spatial_microbiome_soil_climate/scripts

Scripts workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `output/`
- `run_example.py`
- `run_spatial_integration.py`

## Public Interface

- `run_example.py:setup_logging` (function)
- `run_example.py:ClimateAnalysisSystem` (class)
- `run_example.py:main` (function)
- `run_spatial_integration.py:SpatialMicrobiomeIntegrator` (class)
- `run_spatial_integration.py:main` (function)

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
- `h3>=4.5.0,<5`
- `requests>=2.28.0`
- `rich>=12.0.0`
- `typer>=0.7.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module EXAMPLES
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
