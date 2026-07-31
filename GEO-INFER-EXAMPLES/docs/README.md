# GEO-INFER-EXAMPLES/docs

Docs workspace within `GEO-INFER-EXAMPLES`.

## Contents

- `API_INTEGRATION_GUIDE.md`
- `COMPREHENSIVE_DOCUMENTATION_ANALYSIS.md`
- `COMPREHENSIVE_TECHNICAL_SUMMARY.md`
- `CROSS_MODULE_REFERENCE.md`
- `INTEGRATION_EXECUTION_REPORT.md`
- `INTEGRATION_GUIDE.md`
- `PERFORMANCE_BENCHMARKING_GUIDE.md`
- `TECHNICAL_ARCHITECTURE_GUIDE.md`
- `index.md`

## Public Interface

- No public Python symbols are defined directly in this directory.

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
