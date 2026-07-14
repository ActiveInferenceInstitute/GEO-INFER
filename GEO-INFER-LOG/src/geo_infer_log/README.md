# GEO-INFER-LOG/src/geo_infer_log

Geo Infer Log workspace within `GEO-INFER-LOG`.

## Contents

- `api/`
- `core/`
- `models/`
- `utils/`
- `__init__.py`

## Public Interface

- `__init__.py:LogEntry` (class)
- `__init__.py:SpatialLogContext` (class)
- `__init__.py:PerformanceMetrics` (class)
- `__init__.py:EnhancedLogger` (class)
- `__init__.py:JSONFormatter` (class)
- `__init__.py:LogAnalyzer` (class)
- `__init__.py:get_logger` (function)

## Module Metadata

- Module: `GEO-INFER-LOG`
- Package: `geo_infer_log`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-LOG`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG`

## Dependencies

- `pandas>=1.3.0`
- `geopandas>=0.10.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
