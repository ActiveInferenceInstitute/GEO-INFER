# connectors

## Overview

Data source connectors for GEO-INFER-DATA including cloud storage, databases, APIs, files, and streaming services.

This directory contains connectors for diverse geospatial data sources enabling multi-source data ingestion.

## Components

### api.py
API connectors for geospatial web services.

**Classes**: `APIConnector`, `GraphQLConnector`, `STACConnector`

### cloud.py
Cloud storage connectors.

**Classes**: `CloudConnector`, `S3Connector`, `GCSConnector`, `AzureConnector`

### database.py
Database connectors for geospatial data.

**Classes**: `DatabaseConnector`, `PostgreSQLConnector`, `MySQLConnector`, `MongoDBConnector`

### file.py
File system connectors for geospatial data formats.

**Classes**: `FileConnector`, `StreamingFileConnector`

### stream.py
Streaming data connectors.

**Classes**: `StreamConnector`, `MQTTConnector`, `KafkaConnector`, `WebSocketConnector`

## Usage

```python
from geo_infer_data.connectors import STACConnector, PostgreSQLConnector, S3Connector

# STAC connector
stac = STACConnector(url='https://stac.example.com')
results = await stac.search(bbox=[-122.5, 37.7, -122.3, 37.9])

# Database connector
pg = PostgreSQLConnector(host='localhost', database='geospatial_db')
data = await pg.fetch_data(query='SELECT * FROM features WHERE ...')

# Cloud connector
s3 = S3Connector(bucket_name='geospatial-data', region='us-west-2')
data = await s3.fetch_data('path/to/data.geojson')
```

## Integration

- **Location**: `GEO-INFER-DATA/src/geo_infer_data/connectors`
- **Used By**: Core ingestion module for multi-source data access
- **Dependencies**: Various client libraries (boto3, psycopg2, pymongo, etc.)
- **Provides**: Connectors for diverse geospatial data sources

--- 