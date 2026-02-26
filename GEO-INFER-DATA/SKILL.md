---
name: geo-infer-data
description: Data connectors, ETL pipelines, and data management for geospatial datasets. Use when loading spatial data from databases, APIs, files (GeoJSON, Shapefile, GeoParquet), or building data transformation pipelines.
prerequisites:
  required: []
  recommended:
    - geo-infer-math
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-DATA

## Instructions

### Core Capabilities

- **Connectors**: PostgreSQL/PostGIS, SQLite/SpatiaLite, REST APIs, file I/O
- **Formats**: GeoJSON, Shapefile, GeoParquet, GeoTIFF, CSV with coordinates
- **ETL pipelines**: Extract → Transform → Load with spatial awareness
- **Caching**: Spatial tile caching, query result caching
- **Validation**: Schema validation, coordinate bounds checking

### Key Imports

```python
from geo_infer_data.connectors.database import DatabaseConnector
from geo_infer_data.core.pipeline import ETLPipeline
from geo_infer_data.formats.geojson import GeoJSONLoader
```

## Examples

```python
from geo_infer_data.formats.geojson import GeoJSONLoader
from geo_infer_data.core.validation import CoordinateValidator

loader = GeoJSONLoader()
features = loader.load("buildings.geojson")
print(f"Loaded {len(features)} features")

# Validate coordinates against WGS84 bounds
validator = CoordinateValidator()
valid, invalid = validator.validate(features)
print(f"Valid: {len(valid)}, Out-of-bounds: {len(invalid)}")
```

```python
from geo_infer_data.core.pipeline import ETLPipeline

pipeline = ETLPipeline(name="census_ingest")
pipeline.extract(source="postgresql://db/census", query="SELECT * FROM tracts")
pipeline.transform(operations=["reproject_to_4326", "validate_bounds"])
pipeline.load(target="geoparquet", path="output/census.parquet")
pipeline.run()
```

## Guidelines

- SQL uses parameterized queries (`:param` placeholders) — never string interpolation
- All coordinate data validated against WGS84 bounds
- Test: `uv run python -m pytest GEO-INFER-DATA/tests/ -v`

### Integrations

- **SPACE** → Spatial indexing of loaded datasets
- **GIT** → Version control for spatial data
- **API** → Data source for spatial query endpoints
- **IOT** → Sensor data ingestion pipelines
- **EXAMPLES** → Example ETL workflows
