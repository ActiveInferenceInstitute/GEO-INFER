# GEO-INFER-DATA/src/geo_infer_data/connectors

Connectors workspace within `GEO-INFER-DATA`.

## Contents

- `__init__.py`
- `api.py`
- `cloud.py`
- `database.py`
- `file.py`
- `stream.py`

## Public Interface

- `api.py:APIConnector` (class)
- `api.py:GraphQLConnector` (class)
- `api.py:STACConnector` (class)
- `cloud.py:CloudConnector` (class)
- `cloud.py:S3Connector` (class)
- `cloud.py:GCSConnector` (class)
- `cloud.py:AzureConnector` (class)
- `database.py:DatabaseConnector` (class)
- `database.py:PostgreSQLConnector` (class)
- `database.py:MySQLConnector` (class)
- `database.py:MongoDBConnector` (class)
- `file.py:FileConnector` (class)
- `file.py:StreamingFileConnector` (class)
- `stream.py:StreamConnector` (class)
- `stream.py:MQTTConnector` (class)
- `stream.py:KafkaConnector` (class)
- `stream.py:WebSocketConnector` (class)

## Module Metadata

- Module: `GEO-INFER-DATA`
- Package: `geo_infer_data`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-DATA`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module DATA`

## Dependencies

- `geopandas>=0.13.0`
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `shapely>=2.0.0`
- `rasterio>=1.3.0`
- `fiona>=1.9.0`
- `pyproj>=3.5.0`
- `scipy>=1.10.0`
- `scikit-learn>=1.3.0`
- `pyyaml>=6.0.0`
- `openpyxl>=3.1.0`
- `xlrd>=2.0.1`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module DATA
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
