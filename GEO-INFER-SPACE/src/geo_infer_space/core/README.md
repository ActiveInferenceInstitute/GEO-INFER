# GEO-INFER-SPACE/src/geo_infer_space/core

Core workspace within `GEO-INFER-SPACE`.

## Contents

- `__init__.py`
- `analytics.py`
- `api_clients.py`
- `base_module.py`
- `data_integrator.py`
- `dispatcher.py`
- `geometric_operations.py`
- `interfaces.py`
- `place_analyzer.py`
- `processor.py`
- `spatial_indexing.py`
- `spatial_methods.py`
- `spatial_processor.py`
- `statistics.py`
- `unified_backend.py`
- `visualization_engine.py`

## Public Interface

- `analytics.py:SpatialAnalyticsInterface` (class)
- `api_clients.py:BaseAPIManager` (class)
- `api_clients.py:GeneralGeoDataFetcher` (class)
- `base_module.py:BaseAnalysisModule` (class)
- `data_integrator.py:DataIntegrator` (class)
- `dispatcher.py:SpatialBackendInterface` (class)
- `dispatcher.py:SpatialIndexingBackend` (class)
- `dispatcher.py:SpatialAnalyticsBackend` (class)
- `dispatcher.py:SpatialBackendDispatcher` (class)
- `dispatcher.py:get_backend_dispatcher` (function)
- `dispatcher.py:configure_backends` (function)
- `dispatcher.py:reset_dispatcher` (function)
- `geometric_operations.py:GeometricOperationsInterface` (class)
- `interfaces.py:SpatialBackendProtocol` (class)
- `interfaces.py:IndexingBackendProtocol` (class)
- `interfaces.py:AnalyticsBackendProtocol` (class)
- `interfaces.py:H3UnavailableError` (class)
- `interfaces.py:SRAIUnavailableError` (class)
- `interfaces.py:BackendNotAvailableError` (class)
- `place_analyzer.py:PlaceAnalyzer` (class)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

## Dependencies

- `fastapi>=0.68.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=0.4.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
