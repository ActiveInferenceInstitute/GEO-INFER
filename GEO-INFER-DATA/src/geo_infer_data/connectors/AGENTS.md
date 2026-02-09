# Agent
: connectors

## Scope
 This agent handles data source connectors for GEO-INFER-DATA including cloud storage, databases, APIs, files, and streaming services.

## Implementation
 Status

### Currently
 Implemented - ✅ **Cloud Connectors**: `S3Connector`, `GCSConnector`, `AzureConnector` - ✅ **Database Connectors**: `PostgreSQLConnector`, `MySQLConnector`, `MongoDBConnector` - ✅ **API Connectors**: `STACConnector`, `GraphQLConnector`, `APIConnector` - ✅ **File Connectors**: `FileConnector`, `StreamingFileConnector` - ✅ **Stream Connectors**: `MQTTConnector`, `KafkaConnector`, `WebSocketConnector`

## Agent
 Capabilities

### 1
. Cloud Storage Connectors ```python from geo_infer_data.connectors import S3Connector, GCSConnector, AzureConnector

# AWS S3 connector s3 = S3Connector( bucket_name='geospatial-data', region='us-west-2', access_key_id='...', secret_access_key='...' ) data = await s3.fetch_data('path/to/data.geojson')

# Google Cloud Storage connector gcs = GCSConnector( bucket_name='geospatial-data', project_id='my-project', credentials_path='path/to/credentials.json' ) data = await gcs.fetch_data('path/to/data.geojson')

# Azure Blob Storage connector azure = AzureConnector( account_name='storage-account', container_name='geospatial-data', account_key='...' ) data = await azure.fetch_data('path/to/data.geojson') ```

### 2
. Database Connectors ```python from geo_infer_data.connectors import PostgreSQLConnector, MySQLConnector, MongoDBConnector

# PostgreSQL/PostGIS connector pg = PostgreSQLConnector( host='localhost', port=5432, database='geospatial_db', user='user', password='password' ) data = await pg.fetch_data( query='SELECT * FROM features WHERE ST_Within(geom, ST_MakeEnvelope(-122.5, 37.7, -122.3, 37.9, 4326))' )

# MySQL connector mysql = MySQLConnector( host='localhost', port=3306, database='geospatial_db', user='user', password='password' ) data = await mysql.fetch_data(query='SELECT * FROM features WHERE ...')

# MongoDB connector mongo = MongoDBConnector( connection_string='mongodb://localhost:27017', database='geospatial_db', collection='features' ) data = await mongo.fetch_data(filter={'location': {'$geoWithin': {...}}}) ```

### 3
. API Connectors ```python from geo_infer_data.connectors import STACConnector, GraphQLConnector, APIConnector

# STAC connector stac = STACConnector(url='https://stac.example.com') results = await stac.search( bbox=[-122.5, 37.7, -122.3, 37.9], datetime='2023-01-01/2023-12-31', collections=['sentinel-2'] )

# GraphQL connector graphql = GraphQLConnector(url='https://api.example.com/graphql') data = await graphql.query( query=''' query { features(bbox: [-122.5, 37.7, -122.3, 37.9]) { id geometry properties } } ''' )

# Generic API connector api = APIConnector(base_url='https://api.example.com') data = await api.fetch_data(endpoint='/geospatial/data', params={'bbox': '...'}) ```

### 4
. File Connectors ```python from geo_infer_data.connectors import FileConnector, StreamingFileConnector

# File connector file_connector = FileConnector(base_path='/path/to/data') files = file_connector.list_files(pattern='*.geojson', recursive=True) data = await file_connector.fetch_data('data.geojson')

# Streaming file connector for large files streaming = StreamingFileConnector(base_path='/path/to/large/data') async for chunk in streaming.stream_data('large_file.geotiff'): process_chunk(chunk) ```

### 5
. Streaming Connectors ```python from geo_infer_data.connectors import MQTTConnector, KafkaConnector, WebSocketConnector

# MQTT connector mqtt = MQTTConnector( broker='mqtt.example.com', port=1883, topics=['sensors/temperature', 'sensors/humidity'] ) async for message in mqtt.stream(): process_sensor_data(message)

# Kafka connector kafka = KafkaConnector( bootstrap_servers=['kafka1:9092', 'kafka2:9092'], topics=['geospatial-events'] ) async for event in kafka.stream(): process_event(event)

# WebSocket connector ws = WebSocketConnector(url='ws://example.com/geospatial-stream') async for message in ws.stream(): process_realtime_data(message) ```

## Key
 Classes

### CloudConnector
 (Base) Base class for cloud storage connectors. **Subclasses**: `S3Connector`, `GCSConnector`, `AzureConnector`

### DatabaseConnector
 (Base) Base class for database connectors. **Subclasses**: `PostgreSQLConnector`, `MySQLConnector`, `MongoDBConnector`

### APIConnector
 (Base) Base class for API connectors. **Subclasses**: `STACConnector`, `GraphQLConnector`

### FileConnector
 Universal file connector for geospatial data formats.

**Methods**: `list_files(pattern, recursive, file_types) -> List[Path]`, `fetch_data(path) -> Any`

### StreamConnector
 (Base) Base class for streaming data connectors. **Subclasses**: `MQTTConnector`, `KafkaConnector`, `WebSocketConnector`

## Integration

- **Location**: `GEO-INFER-DATA/src/geo_infer_data/connectors`
- **Used By**: Core ingestion module for multi-source data access
- **Dependencies**: Various client libraries (boto3, psycopg2, pymongo, etc.)
- **Provides**: Connectors for diverse geospatial data sources --- This AGENTS.md documents data source connectors for GEO-INFER-DATA.
