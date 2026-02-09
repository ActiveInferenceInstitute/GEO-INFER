# Agent
: core

## Scope
 This directory contains core components for the module. It provides 26 classes and 0 functions.

## Classes
 and Functions

### IngestionConfig
 Configuration for data ingestion.

### DataSourceConnector
 Base class for data source connectors.

### SatelliteDataConnector
 Connector for satellite imagery data sources.

### SensorDataConnector
 Connector for IoT sensor data.

### CrowdsourcedDataConnector
 Connector for crowdsourced data.

### MultiSourceDataIngestion
 Multi-source geospatial data ingestion system.

**Methods**:
- `generate_quality_report(data: Dict[str, Any]) -> Dict[str, Any]`: Generate quality report for ingested data.

### PipelineStatus
 Pipeline execution status.

### ErrorRecoveryStrategy
 Error recovery strategies.

### PipelineMetrics
 Pipeline execution metrics.

### TransformationEngine
 Engine for executing data transformations.

### IntelligentETLPipeline
 ETL pipeline with automatic dependency resolution and error recovery.

**Methods**:
- `get_performance_metrics() -> Dict[str, Any]`: Get pipeline performance metrics.
- `identify_bottlenecks(metrics: Dict[str, Any]) -> List[str]`: Identify performance bottlenecks.

### OptimizationStrategy
 Storage optimization strategies.

### IndexingStrategy
 Spatial indexing strategies.

### StorageConfig
 Storage system configuration.

### AccessPattern
 Data access pattern analysis.

### StorageBackendManager
 Manager for different storage backends.

### PostgreSQLBackend
 PostgreSQL/PostGIS storage backend.

### MinIOBackend
 MinIO/S3 object storage backend.

### RedisBackend
 Redis caching and storage backend.

### LocalFileBackend
 Local file system storage backend.

### AdaptiveDataStorage
 Adaptive data storage with automatic optimization based on access patterns.

**Methods**:
- `optimize_for_patterns(patterns: Dict[str, Any], time_window: str) -> Dict[str, Any]`: Optimize storage based on access patterns.
- `get_storage_stats() -> Dict[str, Any]`: Get storage statistics.

### ValidationLevel
 Validation strictness levels.

### ValidationRule
 Available validation rules.

### ValidationConfig
 Configuration for data validation.

### GeospatialValidator
 geospatial data validation.

### DataQualityManager
 data quality management and validation.

**Methods**:
- `get_improvement_recommendations(report: DataQualityReport) -> List[str]`: Get improvement recommendations based on quality report.
- `get_quality_trends(days: int) -> Dict[str, Any]`: Get quality trends over time.

## Capabilities

- **26 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-DATA/src/geo_infer_data/core`
- **Type**: Directory Node
