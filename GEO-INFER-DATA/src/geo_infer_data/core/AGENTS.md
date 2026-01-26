# Agent
: core ## Scope
 This directory contains core components for the module. It provides 26 classes and 0 functions. ## Classes
 and Functions ### IngestionConfi
g
 Configuration for data ingestion. ### DataSourceConnecto
r
 Base class for data source connectors. ### SatelliteDataConnecto
r
 Connector for satellite imagery data sources. ### SensorDataConnecto
r
 Connector for IoT sensor data. ### CrowdsourcedDataConnecto
r
 Connector for crowdsourced data. ### MultiSourceDataIngestio
n
 Multi-source geospatial data ingestion system. **Methods**: - `generate_quality_report(data: Dict[str, Any]) -> Dict[str, Any]`: Generate quality report for ingested data. ### PipelineStatu
s
 Pipeline execution status. ### ErrorRecoveryStrateg
y
 Error recovery strategies. ### PipelineMetric
s
 Pipeline execution metrics. ### TransformationEngin
e
 Engine for executing data transformations. ### IntelligentETLPipelin
e
 ETL pipeline with automatic dependency resolution and error recovery. **Methods**: - `get_performance_metrics() -> Dict[str, Any]`: Get pipeline performance metrics. - `identify_bottlenecks(metrics: Dict[str, Any]) -> List[str]`: Identify performance bottlenecks. ### OptimizationStrateg
y
 Storage optimization strategies. ### IndexingStrateg
y
 Spatial indexing strategies. ### StorageConfi
g
 Storage system configuration. ### AccessPatter
n
 Data access pattern analysis. ### StorageBackendManage
r
 Manager for different storage backends. ### PostgreSQLBacken
d
 PostgreSQL/PostGIS storage backend. ### MinIOBacken
d
 MinIO/S3 object storage backend. ### RedisBacken
d
 Redis caching and storage backend. ### LocalFileBacken
d
 Local file system storage backend. ### AdaptiveDataStorag
e
 Adaptive data storage with automatic optimization based on access patterns. **Methods**: - `optimize_for_patterns(patterns: Dict[str, Any], time_window: str) -> Dict[str, Any]`: Optimize storage based on access patterns. - `get_storage_stats() -> Dict[str, Any]`: Get storage statistics. ### ValidationLeve
l
 Validation strictness levels. ### ValidationRul
e
 Available validation rules. ### ValidationConfi
g
 Configuration for data validation. ### GeospatialValidato
r
 geospatial data validation. ### DataQualityManage
r
 data quality management and validation. **Methods**: - `get_improvement_recommendations(report: DataQualityReport) -> List[str]`: Get improvement recommendations based on quality report. - `get_quality_trends(days: int) -> Dict[str, Any]`: Get quality trends over time. ## Capabilities
 - **26 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-DATA/src/geo_infer_data/core` - **Type**: Directory Node 