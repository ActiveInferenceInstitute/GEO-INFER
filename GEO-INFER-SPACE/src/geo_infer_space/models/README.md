# GEO-INFER-SPACE/src/geo_infer_space/models

Models workspace within `GEO-INFER-SPACE`.

## Contents

- `__init__.py`
- `config_models.py`
- `data_models.py`

## Public Interface

- `config_models.py:DatabaseConfig` (class)
- `config_models.py:IndexingConfig` (class)
- `config_models.py:AnalysisConfig` (class)
- `config_models.py:APIConfig` (class)
- `config_models.py:LoggingConfig` (class)
- `config_models.py:CacheConfig` (class)
- `config_models.py:OSCConfig` (class)
- `config_models.py:SpaceConfig` (class)
- `config_models.py:PerformanceConfig` (class)
- `data_models.py:GeometryType` (class)
- `data_models.py:CoordinateReferenceSystem` (class)
- `data_models.py:GeometryModel` (class)
- `data_models.py:SpatialBounds` (class)
- `data_models.py:SpatialIndex` (class)
- `data_models.py:SpatialMetadata` (class)
- `data_models.py:SpatialDataset` (class)
- `data_models.py:AnalysisResult` (class)
- `data_models.py:H3CellData` (class)
- `data_models.py:NetworkEdge` (class)
- `data_models.py:NetworkNode` (class)

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
- `h3>=4.0.0`
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
