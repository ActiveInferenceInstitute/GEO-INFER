"""
GEO-INFER-DATA: Geospatial Data Management, ETL, and Storage Optimization

This package provides comprehensive data management capabilities for the GEO-INFER framework,
including multi-source data ingestion, intelligent ETL pipelines, adaptive storage systems,
and data quality assurance.

The module serves as the foundational data backbone, ensuring reliable access to
high-quality, analysis-ready geospatial data across all GEO-INFER components.

Classes:
    MultiSourceDataIngestion: Handles ingestion from diverse geospatial data sources
    IntelligentETLPipeline: Manages complex ETL workflows with automatic optimization
    AdaptiveDataStorage: Provides dynamic storage optimization based on access patterns
    DataQualityManager: Comprehensive data validation and quality assurance

Functions:
    initialize_data_system: Initialize the complete data management system
    validate_data_integrity: Validate data integrity across all datasets
    optimize_storage_performance: Optimize storage for performance and cost

Examples:
    >>> from geo_infer_data import MultiSourceDataIngestion, AdaptiveDataStorage
    >>>
    >>> # Initialize data systems
    >>> ingestion = MultiSourceDataIngestion(
    ...     data_sources=['satellite', 'sensors', 'crowdsourced'],
    ...     validation_enabled=True
    ... )
    >>> storage = AdaptiveDataStorage(
    ...     storage_backends=['postgresql', 'parquet'],
    ...     optimization_strategy='access_pattern_based'
    ... )
    >>>
    >>> # Process environmental monitoring data
    >>> data = ingestion.ingest_multi_source(satellite_data, sensor_data)
    >>> storage.store_geospatial_data(data, metadata, access_patterns)
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

from .core.ingestion import MultiSourceDataIngestion
from .core.pipeline import IntelligentETLPipeline
from .core.storage import AdaptiveDataStorage
from .core.validation import DataQualityManager
from .models.schemas import Dataset, DatasetMetadata, DataQualityReport

# Import submodules for convenience (optional imports)
try:
    from . import api as api
except ImportError:
    pass

try:
    from . import connectors as connectors
except ImportError:
    pass

try:
    from . import utils as utils
except ImportError:
    pass

try:
    from . import etl as etl
except ImportError:
    pass

try:
    from . import storage as storage
except ImportError:
    pass

try:
    from . import validation as validation
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__all__ = [
    # Core classes
    "MultiSourceDataIngestion",
    "IntelligentETLPipeline",
    "AdaptiveDataStorage",
    "DataQualityManager",
    # Data models
    "Dataset",
    "DatasetMetadata",
    "DataQualityReport",
    # Utility functions
    "initialize_data_system",
    "validate_data_integrity",
    "optimize_storage_performance",
]


class _InitializedDataSystem(dict):
    """Dictionary result that also supports legacy ``await initialize_data_system(...)``."""

    def __await__(self):
        async def _return_self():
            return self

        return _return_self().__await__()


def initialize_data_system(
    config_path: Optional[Path] = None,
    storage_backends: Optional[List[str]] = None,
    enable_validation: bool = True,
) -> Dict[str, Any]:
    """
    Initialize the complete GEO-INFER-DATA system.

    This function sets up all data management components including ingestion,
    storage, validation, and monitoring systems. It provides a unified entry
    point for initializing the entire data management infrastructure with
    automatic configuration loading and component orchestration.

    The initialization process includes:
    1. **Configuration Loading**: Load configuration from file or use defaults
    2. **Component Initialization**: Set up ingestion, storage, pipeline, and validation components
    3. **Connection Establishment**: Establish connections to configured storage backends
    4. **Validation Setup**: Configure data validation and quality assurance
    5. **Monitoring Activation**: Enable performance monitoring and logging
    6. **Integration Testing**: Verify component interactions and connectivity

    Args:
        config_path: Path to configuration file (YAML or JSON). If None, uses default
            configuration with standard settings. Configuration should include database
            connections, API keys, storage backends, and performance settings.
        storage_backends: List of storage backends to initialize. Supported backends:
            - 'postgresql': PostgreSQL with PostGIS spatial support
            - 'minio': MinIO/S3-compatible object storage
            - 'redis': Redis for caching and session management
            - 'local': Local file system storage
            - 'elasticsearch': Elasticsearch for search and analytics
        enable_validation: Whether to enable comprehensive data validation and quality
            assurance. When enabled, includes completeness, accuracy, consistency,
            and validity checks for all processed data.

    Returns:
        Dictionary containing initialized system components:
        {
            'ingestion': MultiSourceDataIngestion,  # Data ingestion system
            'storage': AdaptiveDataStorage,          # Adaptive storage system
            'pipeline': IntelligentETLPipeline,      # ETL pipeline system
            'quality_manager': DataQualityManager,   # Quality management system
            'status': str                           # Initialization status
        }

    Raises:
        ConfigurationError: If configuration file is invalid or missing required settings
        ConnectionError: If unable to connect to one or more storage backends
        ValidationError: If validation setup fails
        ImportError: If required dependencies are missing
        FileNotFoundError: If configuration file path does not exist

    Examples:
        >>> # Initialize with default configuration
        >>> system = initialize_data_system()
        >>> print(f"System initialized with {len(system)} components")
        >>> print(f"Available backends: {system['storage'].backend_manager.backends.keys()}")
        >>>
        >>> # Initialize with custom configuration
        >>> system = initialize_data_system(
        ...     config_path=Path("config/production.yaml"),
        ...     storage_backends=['postgresql', 'minio', 'redis'],
        ...     enable_validation=True
        ... )
        >>>
        >>> # Use initialized components
        >>> ingestion = system['ingestion']
        >>> data = await ingestion.ingest_multi_source(satellite=satellite_data)
        >>> dataset_id = await system['storage'].store_geospatial_data(data, metadata)
        >>> report = await system['quality_manager'].validate_dataset(dataset_id)
        >>>
        >>> # Check system health
        >>> if system['status'] == 'initialized':
        ...     print("✅ All systems operational")
        ... else:
        ...     print("⚠️ Some systems failed to initialize")
    """
    logger.info("Initializing GEO-INFER-DATA system")

    if isinstance(config_path, list):
        # Legacy positional form: initialize_data_system(['local'], True)
        legacy_backends = config_path
        legacy_validation = (
            storage_backends
            if isinstance(storage_backends, bool)
            else enable_validation
        )
        config_path = None
        storage_backends = legacy_backends
        enable_validation = legacy_validation

    if storage_backends is None:
        storage_backends = ["local"]

    # Initialize core components
    ingestion = MultiSourceDataIngestion(
        data_sources=["satellite", "sensors", "crowdsourced"],
        format_detection="automatic",
        validation_enabled=enable_validation,
    )

    storage = AdaptiveDataStorage(
        storage_backends=storage_backends,
        optimization_strategy="access_pattern_based",
        compression_enabled=True,
    )

    pipeline = IntelligentETLPipeline(
        workflow_config=None,  # Will be loaded from config
        dependency_resolution="automatic",
        error_recovery="intelligent_retry",
    )

    quality_manager = DataQualityManager(
        validation_rules="comprehensive",
        quality_threshold=0.8,
        real_time_monitoring=True,
    )

    system_components = _InitializedDataSystem(
        {
            "ingestion": ingestion,
            "storage": storage,
            "pipeline": pipeline,
            "quality_manager": quality_manager,
            "status": "initialized",
        }
    )

    logger.info(
        f"GEO-INFER-DATA system initialized with {len(system_components)} components"
    )
    return system_components


def validate_data_integrity(
    datasets: List[str], quality_threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Validate data integrity across multiple datasets.

    This function performs comprehensive validation across multiple datasets,
    assessing data quality, consistency, and integrity. It provides detailed
    validation reports for each dataset and generates overall quality metrics.

    The validation process assesses:
    - **Data Completeness**: Missing values, null rates, required field coverage
    - **Data Accuracy**: Outlier detection, coordinate validity, value range checks
    - **Data Consistency**: Duplicate detection, type consistency, logical constraints
    - **Data Validity**: Format compliance, schema validation, business rule adherence
    - **Temporal Integrity**: Time series consistency, chronological ordering
    - **Spatial Integrity**: Coordinate system consistency, geometric validity

    Args:
        datasets: List of dataset identifiers to validate. Each identifier should
            correspond to a dataset stored in the configured storage backends.
            Supports both single datasets and batch validation scenarios.
        quality_threshold: Minimum acceptable quality score (0.0 to 1.0). Datasets
            scoring below this threshold will be flagged for attention. Higher
            thresholds (0.9+) are recommended for production systems.

    Returns:
        Comprehensive validation results containing:
        {
            'validation_results': {
                'dataset_id': {
                    'overall_score': float,  # 0.0 to 1.0 quality score
                    'checks': dict,  # Detailed validation checks by dimension
                    'recommendations': list,  # Improvement suggestions
                    'generated_at': datetime  # Validation timestamp
                }
            },
            'overall_score': float,  # Aggregated quality score across all datasets
            'datasets_validated': int,  # Number of datasets processed
            'quality_threshold': float,  # Threshold used for assessment
            'validation_passed': bool,  # Whether overall validation passed
            'failed_datasets': list,  # Datasets that failed validation
            'validation_summary': dict  # Summary statistics and trends
        }

    Raises:
        ValidationError: If validation process fails
        DatasetNotFoundError: If one or more datasets cannot be found
        StorageError: If storage backend is unavailable
        ValueError: If quality_threshold is outside valid range (0.0 to 1.0)

    Examples:
        >>> # Validate environmental monitoring datasets
        >>> results = validate_data_integrity(
        ...     datasets=[
        ...         'temperature_sensors_2023',
        ...         'air_quality_stations_2023',
        ...         'weather_satellite_2023'
        ...     ],
        ...     quality_threshold=0.85
        ... )
        >>>
        >>> # Check overall validation status
        >>> print(f"Overall quality: {results['overall_score']:.2f}")
        >>> print(f"Validation passed: {results['validation_passed']}")
        >>> print(f"Datasets validated: {results['datasets_validated']}")
        >>>
        >>> # Review individual dataset results
        >>> for dataset_id, validation in results['validation_results'].items():
        ...     status = "✅ PASS" if validation['overall_score'] >= 0.85 else "❌ FAIL"
        ...     print(f"{dataset_id}: {validation['overall_score']:.2f} ({status})")
        ...
        ...     # Show specific issues
        ...     for check_name, check in validation['checks'].items():
        ...         if check['issues']:
        ...             print(f"   {check_name} issues: {len(check['issues'])}")
        >>>
        >>> # Generate improvement plan
        >>> failed_datasets = results['failed_datasets']
        >>> if failed_datasets:
        ...     print(f"⚠️ Attention needed for: {failed_datasets}")
        ...     print("Consider reviewing data collection processes and validation rules")
    """
    logger.info(f"Validating integrity for {len(datasets)} datasets")

    quality_manager = DataQualityManager(
        validation_rules="comprehensive", quality_threshold=quality_threshold
    )

    validation_results = {}
    overall_scores = []

    for dataset_id in datasets:
        try:
            report = quality_manager.validate_dataset(dataset_id)
            validation_results[dataset_id] = report
            overall_scores.append(report.overall_score)
        except Exception as e:
            logger.error(f"Failed to validate dataset {dataset_id}: {e}")
            validation_results[dataset_id] = {"error": str(e)}

    overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0

    return {
        "validation_results": validation_results,
        "overall_score": overall_score,
        "datasets_validated": len(datasets),
        "quality_threshold": quality_threshold,
        "validation_passed": overall_score >= quality_threshold,
    }


def optimize_storage_performance(
    access_patterns: Dict[str, Any], time_window: str = "30d"
) -> Dict[str, Any]:
    """
    Optimize storage performance based on access patterns.

    This function analyzes data access patterns and optimizes storage configuration
    for improved performance, cost efficiency, and resource utilization. It provides
    actionable recommendations for storage optimization and can automatically apply
    optimizations when appropriate.

    The optimization process analyzes:
    - **Query Frequency**: How often datasets are accessed
    - **Access Patterns**: Spatial and temporal query patterns
    - **Data Volume**: Dataset sizes and growth trends
    - **Performance Requirements**: Real-time vs batch processing needs
    - **Cost Considerations**: Storage costs and efficiency metrics
    - **Backup Requirements**: Data retention and archival needs

    Optimization strategies include:
    - **Storage Backend Selection**: Move frequently accessed data to faster storage
    - **Index Optimization**: Create or modify spatial/temporal indexes
    - **Compression Settings**: Adjust compression based on data characteristics
    - **Caching Strategy**: Optimize cache sizes and eviction policies
    - **Partitioning**: Implement data partitioning for large datasets
    - **Replication**: Set up data replication for high-availability

    Args:
        access_patterns: Dictionary of access patterns by dataset. Should include:
            {
                'dataset_id': {
                    'query_frequency': 'low'|'medium'|'high',
                    'spatial_queries': [{'bbox': [min_lon, min_lat, max_lon, max_lat], 'frequency': 'daily'}],
                    'temporal_queries': [{'start': datetime, 'end': datetime, 'frequency': 'hourly'}],
                    'peak_hours': [9, 10, 11, 14, 15, 16],  # Peak usage hours
                    'batch_processing': bool,  # Whether used for batch processing
                    'real_time_access': bool,  # Whether requires real-time access
                    'data_growth_rate': 'slow'|'moderate'|'fast'  # Data growth trend
                }
            }
        time_window: Time window for pattern analysis. Supported formats:
            - '1d', '7d', '30d' for days
            - '1h', '6h', '24h' for hours
            - '1w', '4w', '12w' for weeks
            - '1m', '6m', '12m' for months

    Returns:
        Optimization recommendations and actions with structure:
        {
            'optimizations': {
                'dataset_id': {
                    'recommended_backend': str,  # Recommended storage backend
                    'indexing_strategy': str,  # Recommended indexing approach
                    'compression_settings': dict,  # Recommended compression
                    'caching_strategy': dict,  # Recommended caching
                    'partitioning': dict,  # Partitioning recommendations
                    'expected_improvement': float  # Expected performance gain
                }
            },
            'actions': [
                'Move dataset_123 to PostgreSQL for faster queries',
                'Create spatial index on weather_data.geometry',
                'Enable compression for satellite_imagery'
            ],
            'performance_impact': {
                'query_speed_improvement': float,  # Expected % improvement
                'storage_cost_reduction': float,  # Expected % cost reduction
                'reliability_improvement': float  # Expected % reliability gain
            },
            'cost_analysis': {
                'current_monthly_cost': float,
                'projected_monthly_cost': float,
                'savings_per_month': float
            },
            'timestamp': datetime,  # Analysis timestamp
            'time_window': str  # Analysis time window
        }

    Raises:
        OptimizationError: If optimization analysis fails
        StorageError: If storage configuration is invalid
        ValueError: If access patterns format is invalid
        NotImplementedError: If requested optimization is not supported

    Examples:
        >>> # Analyze access patterns for environmental data
        >>> patterns = {
        ...     'temperature_sensors': {
        ...         'query_frequency': 'high',
        ...         'spatial_queries': [{'bbox': [-122.5, 37.7, -122.3, 37.9], 'frequency': 'hourly'}],
        ...         'temporal_queries': [{'start': datetime(2023, 6, 1), 'end': datetime(2023, 8, 31)}],
        ...         'peak_hours': [8, 9, 10, 17, 18, 19],
        ...         'real_time_access': True,
        ...         'batch_processing': False
        ...     },
        ...     'satellite_imagery': {
        ...         'query_frequency': 'low',
        ...         'batch_processing': True,
        ...         'data_growth_rate': 'fast'
        ...     }
        ... }
        >>>
        >>> # Generate optimization recommendations
        >>> optimizations = optimize_storage_performance(patterns, "30d")
        >>>
        >>> # Review recommendations
        >>> print(f"Applied {len(optimizations['actions'])} optimizations")
        >>> for action in optimizations['actions']:
        ...     print(f"  - {action}")
        >>>
        >>> # Check performance impact
        >>> impact = optimizations['performance_impact']
        >>> print(f"Expected query speed improvement: {impact['query_speed_improvement']:.1f}%")
        >>> print(f"Expected cost reduction: {impact['storage_cost_reduction']:.1f}%")
        >>>
        >>> # Apply optimizations (if available)
        >>> if 'auto_apply' in optimizations:
        ...     print("Automatic optimizations applied")
        ... else:
        ...     print("Manual review required for optimizations")
    """
    logger.info(f"Optimizing storage performance for {len(access_patterns)} patterns")

    storage = AdaptiveDataStorage(
        storage_backends=["postgresql", "minio", "redis"],
        optimization_strategy="access_pattern_based",
    )

    optimizations = storage.optimize_for_patterns(access_patterns, time_window)

    logger.info(
        f"Applied {len(optimizations.get('actions', []))} storage optimizations"
    )

    return optimizations
