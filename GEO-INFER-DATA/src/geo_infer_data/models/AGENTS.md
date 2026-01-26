# Agent
: models ## Scope
 This agent handles data models and schemas for GEO-INFER-DATA using Pydantic for validation, serialization, and type safety. ## Implementation
 Status ### Currentl
y
 Implemented - ✅ **Dataset Models**: `Dataset`, `DatasetMetadata`, `DatasetSummary` - ✅ **Quality Models**: `DataQualityReport`, `QualityCheck`, `QualityStatus` - ✅ **Spatial/Temporal Models**: `SpatialExtent`, `TemporalExtent`, `CoordinateReferenceSystem` - ✅ **ETL Models**: `ETLPipeline`, `DataSource`, `DataDestination`, `Transformation`, `ExecutionStatus` - ✅ **Data Type Enums**: `DataType`, `DataFormat`, `StorageBackend`, `ExecutionState` - ✅ **Lineage Models**: `DataLineage` for data provenance tracking - ✅ **API Models**: `Pagination`, `HealthStatus` for API responses ## Agent
 Capabilities ### 1
. Dataset Models ```python from geo_infer_data.models import Dataset, DatasetMetadata, SpatialExtent, TemporalExtent # Create dataset metadata metadata = DatasetMetadata( title="Temperature Monitoring Data", description="Real-time temperature measurements", spatial=SpatialExtent( bbox=[-122.5, 37.7, -122.3, 37.9], crs="EPSG:4326" ), temporal=TemporalExtent( start="2023-01-01T00:00:00Z", end="2023-12-31T23:59:59Z", resolution="PT1H" ) ) # Create dataset dataset = Dataset( id="temp_monitoring_2023", title="Temperature Monitoring 2023", type=DataType.TIME_SERIES, metadata=metadata ) ``` ### 2
. Quality Models ```python from geo_infer_data.models import DataQualityReport, QualityCheck, QualityStatus # Create quality check check = QualityCheck( category="geometry", status=QualityStatus.PASS, score=0.95, message="All geometries valid" ) # Create quality report report = DataQualityReport( dataset_id="dataset_123", overall_score=0.92, checks={"geometry": check, "completeness": check2} ) ``` ### 3
. ETL Pipeline Models ```python from geo_infer_data.models import ETLPipeline, DataSource, DataDestination, Transformation # Define ETL pipeline pipeline = ETLPipeline( name="environmental_data_pipeline", source=DataSource( type="api", connection="https://api.example.com/data" ), destination=DataDestination( type="postgresql", connection="postgresql://localhost/db" ), transformations=[ Transformation( name="project_to_utm", type="spatial_transform", parameters={"target_crs": "EPSG:32610"} ) ] ) ``` ### 4
. Spatial and Temporal Extents ```python from geo_infer_data.models import SpatialExtent, TemporalExtent # Spatial extent spatial = SpatialExtent( bbox=[-122.5, 37.7, -122.3, 37.9], crs="EPSG:4326" ) # Temporal extent temporal = TemporalExtent( start="2023-01-01T00:00:00Z", end="2023-12-31T23:59:59Z", resolution="PT1H" ) ``` ## Key
 Classes ### Datase
t
 dataset representation with metadata, data type, and quality information. **Fields**: `id`, `title`, `type`, `format`, `metadata`, `quality` ### DatasetMetadat
a
 metadata including spatial/temporal extents, lineage, and quality checks. **Fields**: `title`, `description`, `spatial`, `temporal`, `lineage`, `quality`, `version` ### DataQualityRepor
t
 Quality assessment results with overall score and individual check results. **Fields**: `dataset_id`, `overall_score`, `checks`, `timestamp` ### SpatialExten
t
 Geographic bounds and coordinate reference system. **Fields**: `bbox`, `crs` **Methods**: `validate_bbox()`, `validate_crs()` ### TemporalExten
t
 Time range and resolution for temporal data. **Fields**: `start`, `end`, `resolution` **Methods**: `validate_temporal_order()` ### ETLPipelin
e
 ETL pipeline configuration with source, destination, and transformations. **Fields**: `name`, `source`, `destination`, `transformations` **Methods**: `sort_transformations()` ### Enum
s
 - `DataType`: VECTOR, RASTER, POINT_CLOUD, TIME_SERIES, NETWORK, TABULAR - `DataFormat`: GEOJSON, SHAPEFILE, GEOPACKAGE, GEOTIFF, NETCDF, CSV, PARQUET, HDF5, ZARR, KML, WKT, WKB - `QualityStatus`: PASS, FAIL, WARNING, UNKNOWN - `StorageBackend`: POSTGRESQL, MINIO, REDIS, ELASTICSEARCH, TIMESCALEDB - `ExecutionState`: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED ## Integration
 - **Location**: `GEO-INFER-DATA/src/geo_infer_data/models` - **Used By**: Core ingestion, pipeline, storage, validation, and API modules - **Dependencies**: `pydantic` for validation - **Provides**: Type-safe data models for the entire data management system --- This AGENTS.md documents data models and schemas for GEO-INFER-DATA. 