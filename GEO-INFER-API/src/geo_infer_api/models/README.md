# GEO-INFER-API/src/geo_infer_api/models

Models workspace within `GEO-INFER-API`.

## Contents

- `__init__.py`
- `geojson.py`

## Public Interface

- `geojson.py:GeoJSONType` (class)
- `geojson.py:GeometryBase` (class)
- `geojson.py:Point` (class)
- `geojson.py:LineString` (class)
- `geojson.py:Polygon` (class)
- `geojson.py:MultiPoint` (class)
- `geojson.py:MultiLineString` (class)
- `geojson.py:MultiPolygon` (class)
- `geojson.py:Feature` (class)
- `geojson.py:FeatureCollection` (class)
- `geojson.py:PolygonFeature` (class)
- `geojson.py:PolygonFeatureCollection` (class)

## Module Metadata

- Module: `GEO-INFER-API`
- Package: `geo_infer_api`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-API`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module API`

## Dependencies

- `fastapi>=0.95.0,<0.96.0`
- `uvicorn>=0.21.0,<0.22.0`
- `pydantic>=1.10.7,<2.0.0`
- `pydantic-settings>=2.0.0,<3.0.0`
- `python-dotenv>=1.0.0,<2.0.0`
- `python-multipart>=0.0.6,<0.1.0`
- `httpx>=0.24.0,<0.25.0`
- `pytest>=7.3.1,<7.4.0`
- `pytest-cov>=4.1.0,<4.2.0`
- `requests>=2.28.2,<2.29.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module API
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
