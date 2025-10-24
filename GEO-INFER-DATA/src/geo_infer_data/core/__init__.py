"""
Core functionality for GEO-INFER-DATA.

This module contains the core data processing, ingestion, storage,
and validation functionality.

Classes:
    MultiSourceDataIngestion: Handles multi-source data ingestion
    IntelligentETLPipeline: Manages ETL workflows
    AdaptiveDataStorage: Provides adaptive storage management
    DataQualityManager: Handles data validation and quality assurance

Functions:
    detect_data_format: Automatically detect data format from file
    validate_geospatial_data: Validate geospatial data integrity
    optimize_data_access: Optimize data access patterns

Examples:
    >>> from geo_infer_data.core import MultiSourceDataIngestion, AdaptiveDataStorage
    >>>
    >>> # Initialize ingestion system
    >>> ingestion = MultiSourceDataIngestion(
    ...     data_sources=['satellite', 'sensors', 'crowdsourced'],
    ...     format_detection='automatic'
    ... )
    >>>
    >>> # Process data
    >>> data = ingestion.ingest_multi_source(
    ...     satellite_data=landsat_imagery,
    ...     sensor_data=weather_stations,
    ...     crowdsourced_data=citizen_reports
    ... )
    >>>
    >>> # Store with optimization
    >>> storage = AdaptiveDataStorage(storage_backends=['postgresql', 'minio'])
    >>> storage.store_geospatial_data(data, metadata, access_patterns)
"""

from .ingestion import MultiSourceDataIngestion
from .pipeline import IntelligentETLPipeline
from .storage import AdaptiveDataStorage
from .validation import DataQualityManager

__all__ = [
    "MultiSourceDataIngestion",
    "IntelligentETLPipeline",
    "AdaptiveDataStorage",
    "DataQualityManager",
]
