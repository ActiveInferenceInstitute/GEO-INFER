# GEO-INFER-DATA: Data Management Engine

> **Explanation**: Understanding Data Management in GEO-INFER
> 
> This module provides comprehensive data management capabilities for geospatial data, including ingestion, storage, validation, and processing pipelines.

## 🎯 What is GEO-INFER-DATA?

GEO-INFER-DATA is the data management engine that provides comprehensive data handling capabilities for geospatial information. It enables:

- **Multi-format Data Support**: Handle various geospatial data formats with advanced validation
- **Data Validation**: Quality control and data integrity checks with comprehensive diagnostics
- **ETL Pipelines**: Extract, transform, and load data workflows with parallel processing
- **Data Versioning**: Track data lineage and changes with semantic versioning
- **Storage Management**: Efficient data storage and retrieval with compression and indexing
- **Real-time Data Streaming**: Real-time data processing and streaming capabilities
- **Data Governance**: Comprehensive data governance and compliance framework
- **Advanced Analytics**: Data analytics and machine learning integration

### Key Concepts

#### Data Formats
The module supports multiple geospatial data formats with advanced validation:

```python
from geo_infer_data import DataManager

# Initialize data manager with advanced features
data_manager = DataManager(
    supported_formats=['geojson', 'shapefile', 'geotiff', 'netcdf', 'parquet', 'hdf5'],
    validation_enabled=True,
    compression_enabled=True,
    parallel_processing=True
)

# Load different data formats with validation
geojson_data = data_manager.load_data(
    'sensors.geojson',
    validation_config={
        'geometry_validation': True,
        'attribute_validation': True,
        'coordinate_system_validation': True
    }
)

shapefile_data = data_manager.load_data(
    'boundaries.shp',
    validation_config={
        'topology_validation': True,
        'attribute_completeness': True
    }
)

raster_data = data_manager.load_data(
    'elevation.tif',
    validation_config={
        'raster_validation': True,
        'metadata_validation': True
    }
)

# Export to different formats with optimization
data_manager.export_data(
    data=processed_data,
    format='geojson',
    optimization_config={
        'compression': True,
        'spatial_indexing': True,
        'metadata_enrichment': True
    }
)
```

#### Data Validation
Comprehensive data quality control with advanced diagnostics:

```python
from geo_infer_data.validation import DataValidator

# Initialize data validator with advanced features
validator = DataValidator(
    validation_levels=['basic', 'comprehensive', 'expert'],
    diagnostics_enabled=True,
    auto_correction=True
)

# Validate spatial data with comprehensive checks
validation_results = validator.validate_spatial_data(
    data=spatial_data,
    checks=[
        'geometry_validity',
        'coordinate_system',
        'attribute_completeness',
        'topology_consistency',
        'spatial_reference',
        'data_quality_metrics'
    ],
    diagnostics_config={
        'detailed_reporting': True,
        'quality_metrics': True,
        'recommendations': True
    }
)

# Validate temporal data with advanced checks
temporal_validation = validator.validate_temporal_data(
    data=temporal_data,
    checks=[
        'timestamp_format',
        'temporal_consistency',
        'missing_values',
        'temporal_gaps',
        'seasonality_validation'
    ],
    diagnostics_config={
        'temporal_analysis': True,
        'gap_detection': True,
        'consistency_metrics': True
    }
)

# Generate comprehensive validation report
report = validator.generate_comprehensive_validation_report(
    validation_results=validation_results,
    report_config={
        'quality_score': True,
        'issue_categorization': True,
        'remediation_suggestions': True,
        'compliance_checking': True
    }
)
```

## 📚 Core Features

### 1. Advanced Data Ingestion

**Purpose**: Load and process data from various sources and formats with comprehensive validation.

```python
from geo_infer_data.ingestion import DataIngestion

# Initialize data ingestion with advanced features
ingestion = DataIngestion(
    supported_sources=['file', 'database', 'api', 'cloud', 'stream'],
    parallel_processing=True,
    validation_enabled=True
)

# Load from file system with validation
file_data = ingestion.load_from_file(
    file_path='data/sensors.geojson',
    format='geojson',
    encoding='utf-8',
    validation_config={
        'schema_validation': True,
        'data_quality_check': True,
        'spatial_validation': True
    }
)

# Load from database with optimization
db_data = ingestion.load_from_database(
    connection_string='postgresql://user:pass@localhost/geo_db',
    query='SELECT * FROM environmental_sensors',
    optimization_config={
        'query_optimization': True,
        'index_utilization': True,
        'parallel_loading': True
    }
)

# Load from API with authentication
api_data = ingestion.load_from_api(
    endpoint='https://api.example.com/sensors',
    authentication={'api_key': 'your_key'},
    format='json',
    rate_limiting=True,
    retry_mechanism=True
)

# Load from cloud storage with streaming
cloud_data = ingestion.load_from_cloud(
    provider='aws_s3',
    bucket='geo-data-bucket',
    key='sensors/2023/sensors.geojson',
    streaming_config={
        'chunk_size': 1000,
        'parallel_download': True,
        'caching': True
    }
)

# Load from real-time streams
stream_data = ingestion.load_from_stream(
    stream_config={
        'stream_type': 'kafka',
        'topics': ['sensor_data', 'environmental_data'],
        'processing_config': {
            'real_time_processing': True,
            'window_size': 300,
            'aggregation': True
        }
    }
)
```

### 2. Advanced Data Processing

**Purpose**: Process and transform data with comprehensive ETL capabilities.

```python
from geo_infer_data.processing import DataProcessingEngine

# Initialize data processing engine with advanced features
processing_engine = DataProcessingEngine(
    processing_types=['etl', 'streaming', 'batch', 'real_time'],
    parallel_processing=True,
    memory_optimization=True
)

# Configure comprehensive processing parameters
processing_config = processing_engine.configure_processing({
    'extraction': {
        'parallel_extraction': True,
        'incremental_loading': True,
        'data_validation': True
    },
    'transformation': {
        'data_cleaning': True,
        'format_conversion': True,
        'spatial_transformation': True,
        'temporal_processing': True
    },
    'loading': {
        'optimized_loading': True,
        'indexing': True,
        'compression': True
    }
})

# Perform comprehensive ETL processing
etl_result = processing_engine.perform_etl_processing(
    source_data=raw_data,
    processing_config=processing_config,
    transformation_rules={
        'data_cleaning': cleaning_rules,
        'format_conversion': conversion_rules,
        'spatial_processing': spatial_rules,
        'temporal_processing': temporal_rules
    }
)

# Perform real-time data processing
streaming_result = processing_engine.process_real_time_data(
    data_stream=real_time_stream,
    processing_config={
        'window_processing': True,
        'aggregation': True,
        'anomaly_detection': True,
        'quality_monitoring': True
    }
)

# Perform batch data processing
batch_result = processing_engine.process_batch_data(
    batch_data=large_dataset,
    processing_config={
        'parallel_processing': True,
        'memory_optimization': True,
        'chunked_processing': True
    }
)
```

### 3. Advanced Data Storage

**Purpose**: Efficient data storage and retrieval with optimization and indexing.

```python
from geo_infer_data.storage import DataStorageEngine

# Initialize data storage engine with advanced features
storage_engine = DataStorageEngine(
    storage_types=['file', 'database', 'cloud', 'distributed'],
    compression_enabled=True,
    indexing_enabled=True
)

# Configure comprehensive storage parameters
storage_config = storage_engine.configure_storage({
    'file_storage': {
        'compression': 'gzip',
        'format_optimization': True,
        'metadata_storage': True
    },
    'database_storage': {
        'spatial_indexing': True,
        'temporal_indexing': True,
        'query_optimization': True
    },
    'cloud_storage': {
        'distributed_storage': True,
        'replication': True,
        'backup_strategy': True
    }
})

# Store data with optimization
storage_result = storage_engine.store_data(
    data=processed_data,
    storage_config=storage_config,
    optimization_config={
        'compression': True,
        'indexing': True,
        'partitioning': True,
        'caching': True
    }
)

# Retrieve data with optimization
retrieved_data = storage_engine.retrieve_data(
    query=retrieval_query,
    optimization_config={
        'query_optimization': True,
        'index_utilization': True,
        'parallel_retrieval': True
    }
)

# Manage data lifecycle
lifecycle_result = storage_engine.manage_data_lifecycle(
    data_policies=lifecycle_policies,
    management_config={
        'archiving': True,
        'backup': True,
        'cleanup': True,
        'versioning': True
    }
)
```

### 4. Advanced Data Validation

**Purpose**: Comprehensive data quality control and validation with diagnostics.

```python
from geo_infer_data.validation import AdvancedDataValidator

# Initialize advanced data validator
advanced_validator = AdvancedDataValidator(
    validation_levels=['basic', 'comprehensive', 'expert'],
    auto_correction=True,
    machine_learning_validation=True
)

# Configure comprehensive validation parameters
validation_config = advanced_validator.configure_validation({
    'spatial_validation': {
        'geometry_validity': True,
        'topology_consistency': True,
        'coordinate_system': True,
        'spatial_reference': True
    },
    'temporal_validation': {
        'timestamp_consistency': True,
        'temporal_gaps': True,
        'seasonality_validation': True,
        'trend_analysis': True
    },
    'attribute_validation': {
        'data_type_consistency': True,
        'value_ranges': True,
        'completeness': True,
        'uniqueness': True
    },
    'quality_validation': {
        'accuracy_assessment': True,
        'precision_analysis': True,
        'reliability_checking': True
    }
})

# Perform comprehensive data validation
validation_result = advanced_validator.validate_comprehensive(
    data=dataset,
    validation_config=validation_config,
    diagnostics_config={
        'detailed_reporting': True,
        'quality_metrics': True,
        'issue_categorization': True,
        'remediation_suggestions': True
    }
)

# Generate quality assessment report
quality_report = advanced_validator.generate_quality_report(
    validation_result=validation_result,
    report_config={
        'quality_score': True,
        'issue_prioritization': True,
        'compliance_checking': True,
        'recommendations': True
    }
)
```

### 5. Data Versioning and Lineage

**Purpose**: Track data lineage and changes with semantic versioning.

```python
from geo_infer_data.versioning import DataVersioningEngine

# Initialize data versioning engine
versioning_engine = DataVersioningEngine(
    versioning_strategy='semantic',
    lineage_tracking=True,
    change_detection=True
)

# Configure versioning parameters
versioning_config = versioning_engine.configure_versioning({
    'version_strategy': 'semantic',
    'lineage_tracking': True,
    'change_detection': True,
    'metadata_tracking': True,
    'audit_trail': True
})

# Create data version
version_result = versioning_engine.create_version(
    data=dataset,
    version_config=versioning_config,
    metadata={
        'description': 'Updated environmental data',
        'author': 'data_scientist',
        'changes': 'Added new sensor data'
    }
)

# Track data lineage
lineage_result = versioning_engine.track_lineage(
    data=dataset,
    lineage_config={
        'source_tracking': True,
        'transformation_tracking': True,
        'dependency_mapping': True
    }
)

# Detect data changes
change_detection = versioning_engine.detect_changes(
    current_data=current_dataset,
    previous_data=previous_dataset,
    detection_config={
        'structural_changes': True,
        'content_changes': True,
        'quality_changes': True
    }
)
```

### 6. Real-time Data Streaming

**Purpose**: Process real-time data streams with advanced analytics.

```python
from geo_infer_data.streaming import RealTimeDataStreaming

# Initialize real-time data streaming
streaming_engine = RealTimeDataStreaming(
    streaming_platforms=['kafka', 'spark', 'flink'],
    real_time_processing=True,
    analytics_enabled=True
)

# Configure streaming parameters
streaming_config = streaming_engine.configure_streaming({
    'stream_platform': 'kafka',
    'processing_type': 'real_time',
    'analytics_enabled': True,
    'quality_monitoring': True
})

# Process real-time data streams
streaming_result = streaming_engine.process_streams(
    data_streams=real_time_streams,
    processing_config={
        'window_processing': True,
        'aggregation': True,
        'anomaly_detection': True,
        'quality_monitoring': True
    }
)

# Generate real-time analytics
real_time_analytics = streaming_engine.generate_real_time_analytics(
    streaming_data=streaming_result,
    analytics_config={
        'trend_analysis': True,
        'pattern_detection': True,
        'predictive_analytics': True
    }
)
```

### 7. Data Governance

**Purpose**: Comprehensive data governance and compliance framework.

```python
from geo_infer_data.governance import DataGovernanceEngine

# Initialize data governance engine
governance_engine = DataGovernanceEngine(
    governance_framework='comprehensive',
    compliance_enabled=True,
    security_enabled=True
)

# Configure governance parameters
governance_config = governance_engine.configure_governance({
    'data_classification': True,
    'access_control': True,
    'privacy_protection': True,
    'compliance_monitoring': True,
    'audit_trail': True
})

# Implement data governance
governance_result = governance_engine.implement_governance(
    data=dataset,
    governance_config=governance_config,
    compliance_config={
        'gdpr_compliance': True,
        'data_protection': True,
        'access_control': True
    }
)

# Monitor compliance
compliance_monitoring = governance_engine.monitor_compliance(
    data=dataset,
    compliance_standards=['gdpr', 'iso27001', 'sox'],
    monitoring_config={
        'continuous_monitoring': True,
        'audit_reporting': True,
        'violation_detection': True
    }
)
```

## 🔧 API Reference

### DataManager

The core data manager class.

```python
class DataManager:
    def __init__(self, supported_formats, validation_enabled=True):
        """
        Initialize data manager.
        
        Args:
            supported_formats (list): Supported data formats
            validation_enabled (bool): Enable data validation
        """
    
    def load_data(self, source, format, validation_config=None):
        """Load data from various sources with validation."""
    
    def export_data(self, data, format, optimization_config=None):
        """Export data to various formats with optimization."""
    
    def process_data(self, data, processing_config):
        """Process data with comprehensive ETL capabilities."""
    
    def validate_data(self, data, validation_config):
        """Validate data with comprehensive quality checks."""
```

### DataValidator

Advanced data validation capabilities.

```python
class DataValidator:
    def __init__(self, validation_levels, diagnostics_enabled=True):
        """
        Initialize data validator.
        
        Args:
            validation_levels (list): Validation levels
            diagnostics_enabled (bool): Enable diagnostics
        """
    
    def validate_spatial_data(self, data, checks, diagnostics_config):
        """Validate spatial data with comprehensive checks."""
    
    def validate_temporal_data(self, data, checks, diagnostics_config):
        """Validate temporal data with advanced checks."""
    
    def generate_validation_report(self, validation_results, report_config):
        """Generate comprehensive validation report."""
```

### DataProcessingEngine

Advanced data processing capabilities.

```python
class DataProcessingEngine:
    def __init__(self, processing_types, parallel_processing=True):
        """
        Initialize data processing engine.
        
        Args:
            processing_types (list): Processing types
            parallel_processing (bool): Enable parallel processing
        """
    
    def perform_etl_processing(self, source_data, processing_config, transformation_rules):
        """Perform comprehensive ETL processing."""
    
    def process_real_time_data(self, data_stream, processing_config):
        """Process real-time data streams."""
    
    def process_batch_data(self, batch_data, processing_config):
        """Process batch data with optimization."""
```

## 🎯 Use Cases

### 1. Environmental Data Management

**Problem**: Manage comprehensive environmental data from multiple sources.

**Solution**: Use advanced data management for environmental data processing.

```python
from geo_infer_data import DataManager
from geo_infer_data.validation import AdvancedDataValidator

# Initialize data management tools
data_manager = DataManager(supported_formats=['geojson', 'netcdf', 'hdf5'])
advanced_validator = AdvancedDataValidator(validation_levels=['comprehensive'])

# Configure environmental data management
environmental_config = data_manager.configure_environmental_data_management({
    'data_sources': ['satellite', 'sensors', 'models', 'observations'],
    'data_formats': ['geojson', 'netcdf', 'hdf5', 'csv'],
    'validation_enabled': True,
    'quality_monitoring': True
})

# Load and validate environmental data
environmental_data = data_manager.load_environmental_data(
    sources=environmental_sources,
    validation_config={
        'spatial_validation': True,
        'temporal_validation': True,
        'quality_validation': True
    }
)

# Process environmental data
processed_environmental_data = data_manager.process_environmental_data(
    data=environmental_data,
    processing_config={
        'format_standardization': True,
        'quality_improvement': True,
        'spatial_processing': True,
        'temporal_processing': True
    }
)
```

### 2. Smart City Data Integration

**Problem**: Integrate diverse data sources for smart city applications.

**Solution**: Use comprehensive data management for smart city data integration.

```python
from geo_infer_data.processing import DataProcessingEngine
from geo_infer_data.streaming import RealTimeDataStreaming

# Initialize data processing tools
processing_engine = DataProcessingEngine(processing_types=['etl', 'streaming'])
streaming_engine = RealTimeDataStreaming(streaming_platforms=['kafka'])

# Configure smart city data integration
smart_city_config = processing_engine.configure_smart_city_integration({
    'data_sources': ['traffic', 'environmental', 'utilities', 'security'],
    'integration_strategy': 'real_time',
    'quality_monitoring': True,
    'analytics_enabled': True
})

# Integrate smart city data
smart_city_integration = processing_engine.integrate_smart_city_data(
    data_sources=smart_city_sources,
    integration_config={
        'real_time_integration': True,
        'quality_monitoring': True,
        'analytics_enabled': True
    }
)

# Process real-time smart city streams
smart_city_streams = streaming_engine.process_smart_city_streams(
    data_streams=smart_city_data_streams,
    processing_config={
        'real_time_processing': True,
        'quality_monitoring': True,
        'analytics_generation': True
    }
)
```

### 3. Scientific Data Management

**Problem**: Manage complex scientific data with comprehensive validation.

**Solution**: Use advanced data management for scientific data processing.

```python
from geo_infer_data.validation import AdvancedDataValidator
from geo_infer_data.versioning import DataVersioningEngine

# Initialize scientific data management tools
advanced_validator = AdvancedDataValidator(validation_levels=['expert'])
versioning_engine = DataVersioningEngine(versioning_strategy='semantic')

# Configure scientific data management
scientific_config = advanced_validator.configure_scientific_data_management({
    'data_types': ['observational', 'model', 'experimental'],
    'validation_standards': ['scientific', 'quality', 'reproducibility'],
    'versioning_enabled': True,
    'lineage_tracking': True
})

# Validate scientific data
scientific_validation = advanced_validator.validate_scientific_data(
    data=scientific_dataset,
    validation_config={
        'scientific_validation': True,
        'quality_assessment': True,
        'reproducibility_checking': True
    }
)

# Version scientific data
scientific_versioning = versioning_engine.version_scientific_data(
    data=scientific_dataset,
    versioning_config={
        'semantic_versioning': True,
        'lineage_tracking': True,
        'reproducibility_tracking': True
    }
)
```

## 🔗 Integration with Other Modules

### GEO-INFER-SPACE Integration

```python
from geo_infer_data import DataManager
from geo_infer_space import SpatialAnalyzer

# Combine data management with spatial analysis
data_manager = DataManager(supported_formats=['geojson', 'shapefile'])
spatial_analyzer = SpatialAnalyzer()

# Use spatial analysis for data validation
spatial_validation = spatial_analyzer.validate_spatial_data(
    data=spatial_dataset,
    validation_config={
        'geometry_validation': True,
        'spatial_consistency': True
    }
)

# Process spatial data with data management
processed_spatial_data = data_manager.process_spatial_data(
    data=spatial_dataset,
    processing_config={
        'spatial_optimization': True,
        'format_standardization': True
    }
)
```

### GEO-INFER-TIME Integration

```python
from geo_infer_data.processing import DataProcessingEngine
from geo_infer_time import TemporalAnalyzer

# Combine data processing with temporal analysis
processing_engine = DataProcessingEngine(processing_types=['etl', 'streaming'])
temporal_analyzer = TemporalAnalyzer()

# Use temporal analysis for data processing
temporal_validation = temporal_analyzer.validate_temporal_data(
    data=temporal_dataset,
    validation_config={
        'temporal_consistency': True,
        'temporal_gaps': True
    }
)

# Process temporal data with data management
processed_temporal_data = processing_engine.process_temporal_data(
    data=temporal_dataset,
    processing_config={
        'temporal_processing': True,
        'quality_improvement': True
    }
)
```

### GEO-INFER-ACT Integration

```python
from geo_infer_data import DataManager
from geo_infer_act import ActiveInferenceModel

# Combine data management with active inference
data_manager = DataManager(supported_formats=['geojson', 'csv'])
active_model = ActiveInferenceModel(
    state_space=['data_quality', 'processing_state'],
    observation_space=['data_observation']
)

# Use active inference for data management decisions
data_quality_state = data_manager.assess_data_quality(dataset)
active_model.update_beliefs({
    'data_quality': data_quality_state,
    'processing_state': current_processing_state
})

# Make data management decisions using active inference
data_decisions = active_model.make_data_management_decisions(
    context=current_data_context,
    available_actions=['validate', 'process', 'store', 'archive']
)
```

## 🚨 Troubleshooting

### Common Issues

**Data loading problems:**
```python
# Diagnose data loading issues
loading_diagnostics = data_manager.diagnose_loading_issues(
    source=data_source,
    diagnostics=['format_compatibility', 'encoding_issues', 'validation_errors']
)

# Implement robust loading
robust_loading = data_manager.implement_robust_loading(
    source=data_source,
    fallback_strategies=['alternative_format', 'partial_loading', 'error_recovery']
)

# Optimize loading performance
optimized_loading = data_manager.optimize_loading_performance(
    source=data_source,
    optimization_config={
        'parallel_loading': True,
        'caching': True,
        'streaming': True
    }
)
```

**Data validation issues:**
```python
# Implement comprehensive validation
comprehensive_validation = advanced_validator.implement_comprehensive_validation(
    data=dataset,
    validation_config={
        'multi_level_validation': True,
        'auto_correction': True,
        'quality_assessment': True
    }
)

# Generate validation recommendations
validation_recommendations = advanced_validator.generate_validation_recommendations(
    validation_results=validation_results,
    recommendation_config={
        'issue_prioritization': True,
        'remediation_suggestions': True,
        'quality_improvement': True
    }
)
```

**Processing performance issues:**
```python
# Optimize processing performance
processing_optimization = processing_engine.optimize_processing_performance(
    processing_config={
        'parallel_processing': True,
        'memory_optimization': True,
        'streaming_optimization': True
    }
)

# Implement distributed processing
distributed_processing = processing_engine.implement_distributed_processing(
    cluster_config={
        'worker_nodes': 4,
        'load_balancing': True,
        'fault_tolerance': True
    }
)
```

## 📊 Performance Optimization

### Efficient Data Processing

```python
# Enable parallel data processing
data_manager.enable_parallel_processing(n_workers=8)

# Enable data caching
data_manager.enable_data_caching(
    cache_size=10000,
    cache_ttl=1800
)

# Enable adaptive data processing
data_manager.enable_adaptive_data_processing(
    adaptation_rate=0.1,
    adaptation_threshold=0.05
)
```

### Advanced Optimization

```python
# Enable distributed data processing
processing_engine.enable_distributed_processing(
    cluster_size=4,
    load_balancing=True
)

# Enable data intelligence
data_manager.enable_data_intelligence(
    intelligence_sources=['data_patterns', 'usage_analytics', 'quality_metrics'],
    update_frequency='real_time'
)
```

## 🔒 Security Considerations

### Data Security
```python
# Enable data encryption
data_manager.enable_data_encryption(
    encryption_method='aes256',
    key_rotation=True
)

# Enable data access control
data_manager.enable_data_access_control(
    authentication='certificate_based',
    authorization='role_based',
    audit_logging=True
)
```

## 🔗 Related Documentation

### Tutorials
- **[Data Management Basics](../getting_started/data_management_basics.md)** - Learn data management fundamentals
- **[Data Validation Tutorial](../getting_started/data_validation_tutorial.md)** - Master data validation techniques
- **[ETL Processing Tutorial](../getting_started/etl_processing_tutorial.md)** - Build ETL data pipelines

### How-to Guides
- **[Environmental Data Management](../examples/environmental_data_management.md)** - Manage environmental data
- **[Smart City Data Integration](../examples/smart_city_data_integration.md)** - Integrate smart city data
- **[Scientific Data Management](../examples/scientific_data_management.md)** - Manage scientific data

### Technical Reference
- **[Data Management API Reference](../api/data_management_reference.md)** - Complete data management API documentation
- **[Data Validation Methods](../api/data_validation_methods.md)** - Available data validation methods
- **[ETL Processing Patterns](../api/etl_processing_patterns.md)** - ETL processing patterns and best practices

### Explanations
- **[Data Management Theory](../data_management_theory.md)** - Deep dive into data management concepts
- **[Data Validation Theory](../data_validation_theory.md)** - Understanding data validation
- **[ETL Processing Theory](../etl_processing_theory.md)** - ETL processing foundations

### Related Modules
- **[GEO-INFER-SPACE](../modules/geo-infer-space.md)** - Spatial analysis capabilities
- **[GEO-INFER-TIME](../modules/geo-infer-time.md)** - Temporal analysis capabilities
- **[GEO-INFER-ACT](../modules/geo-infer-act.md)** - Active inference capabilities
- **[GEO-INFER-SEC](../modules/geo-infer-sec.md)** - Security capabilities

---

**Ready to get started?** Check out the **[Data Management Basics Tutorial](../getting_started/data_management_basics.md)** or explore **[Environmental Data Management Examples](../examples/environmental_data_management.md)**! 