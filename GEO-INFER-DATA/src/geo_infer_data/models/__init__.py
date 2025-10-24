"""
Data models and schemas for GEO-INFER-DATA.

This module contains Pydantic models for data validation, serialization,
and type safety across the data management system.

Classes:
    Dataset: Complete dataset representation
    DatasetMetadata: Comprehensive metadata for datasets
    DataQualityReport: Quality assessment results
    SpatialExtent: Geographic bounds and coordinate system
    TemporalExtent: Time range and resolution
    DataLineage: Data provenance and transformation history

Examples:
    >>> from geo_infer_data.models import Dataset, DatasetMetadata
    >>>
    >>> # Create dataset metadata
    >>> metadata = DatasetMetadata(
    ...     title="Temperature Monitoring Data",
    ...     description="Real-time temperature measurements from weather stations",
    ...     spatial_extent=SpatialExtent(
    ...         bbox=[-122.5, 37.7, -122.3, 37.9],
    ...         crs="EPSG:4326"
    ...     ),
    ...     temporal_extent=TemporalExtent(
    ...         start="2023-01-01T00:00:00Z",
    ...         end="2023-12-31T23:59:59Z",
    ...         resolution="PT1H"
    ...     )
    ... )
    >>>
    >>> # Create dataset
    >>> dataset = Dataset(
    ...     id="temp_monitoring_2023",
    ...     title="Temperature Monitoring 2023",
    ...     type="time_series",
    ...     metadata=metadata
    ... )
"""

from .schemas import (
    Dataset,
    DatasetMetadata,
    DatasetSummary,
    DataQualityReport,
    SpatialExtent,
    TemporalExtent,
    DataLineage,
    QualityCheck,
    DataSource,
    DataDestination,
    Transformation,
    ETLPipeline,
    ExecutionStatus
)

__all__ = [
    "Dataset",
    "DatasetMetadata",
    "DatasetSummary",
    "DataQualityReport",
    "SpatialExtent",
    "TemporalExtent",
    "DataLineage",
    "QualityCheck",
    "DataSource",
    "DataDestination",
    "Transformation",
    "ETLPipeline",
    "ExecutionStatus",
]
