# models

## Overview

Pydantic data models for GEO-INFER-DATA validation and serialization.

This directory contains data models and schemas using Pydantic for type safety, validation, and serialization across the data management system.

## Components

### schemas.py

Pydantic data models for GEO-INFER-DATA validation and serialization.

**Key Classes**:
- `Dataset`, `DatasetMetadata`, `DatasetSummary`: Dataset models
- `DataQualityReport`, `QualityCheck`, `QualityStatus`: Quality models
- `SpatialExtent`, `TemporalExtent`, `CoordinateReferenceSystem`: Spatial/temporal models
- `ETLPipeline`, `DataSource`, `DataDestination`, `Transformation`, `ExecutionStatus`: ETL models
- `DataType`, `DataFormat`, `StorageBackend`, `ExecutionState`: Enum types
- `DataLineage`: Data provenance tracking
- `Pagination`, `HealthStatus`: API models

## Usage

```python
from geo_infer_data.models import Dataset, DatasetMetadata, SpatialExtent

# Create dataset metadata
metadata = DatasetMetadata(
    title="Temperature Monitoring Data",
    spatial=SpatialExtent(bbox=[-122.5, 37.7, -122.3, 37.9], crs="EPSG:4326")
)

# Create dataset
dataset = Dataset(
    id="temp_monitoring_2023",
    title="Temperature Monitoring 2023",
    type=DataType.TIME_SERIES,
    metadata=metadata
)
```

## Integration

- **Location**: `GEO-INFER-DATA/src/geo_infer_data/models`
- **Used By**: Core ingestion, pipeline, storage, validation, and API modules
- **Dependencies**: `pydantic` for validation
- **Provides**: Type-safe data models for the entire data management system

--- 