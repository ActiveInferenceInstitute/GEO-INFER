# api

## Overview

REST API and service interfaces for GEO-INFER-DATA providing programmatic access to data management operations.

This directory contains REST API and service implementations for accessing and managing geospatial data.

## Components

### rest_api.py

REST API implementation for GEO-INFER-DATA using FastAPI.

**Key Classes**:
- `DataAPI`: REST API server for data access and management
- `DatasetAPI`: Dataset-specific API endpoints

### service.py

Core data service for GEO-INFER-DATA.

**Key Classes**:
- `DataService`: Core data service for dataset management and operations

## Usage

```python
from geo_infer_data.api import DataAPI, DataService

# Start API server
api = DataAPI(config_path='config/local.yaml', port=8001)
api.start()

# Use data service
service = DataService()
datasets = await service.list_datasets()
```

## Integration

- **Location**: `GEO-INFER-DATA/src/geo_infer_data/api`
- **Dependencies**: `fastapi`, `uvicorn`, `geo_infer_data.core`, `geo_infer_data.models`
- **Used By**: External applications, web interfaces, other GEO-INFER modules
- **Provides**: REST API interface for data management operations

--- 