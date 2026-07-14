# GEO-INFER-BIO/src/geo_infer_bio/api

Api workspace within `GEO-INFER-BIO`.

## Contents

- `graphql_api.py`
- `rest_api.py`

## Public Interface

- `graphql_api.py:SpatialData` (class)
- `graphql_api.py:SequenceData` (class)
- `graphql_api.py:AnalysisResult` (class)
- `graphql_api.py:VisualizationData` (class)
- `graphql_api.py:Query` (class)
- `rest_api.py:SpatialData` (class)
- `rest_api.py:SequenceData` (class)
- `rest_api.py:AnalysisResult` (class)
- `rest_api.py:root` (function)
- `rest_api.py:analyze_sequence` (function)
- `rest_api.py:analyze_file` (function)
- `rest_api.py:visualize_spatial` (function)
- `rest_api.py:health_check` (function)

## Module Metadata

- Module: `GEO-INFER-BIO`
- Package: `geo_infer_bio`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-BIO`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module BIO`

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


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module BIO
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
