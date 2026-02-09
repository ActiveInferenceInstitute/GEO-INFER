# Agent
: src

## Scope
Agent handles source code implementation for GEO-INFER-SPACE module providing spatial methods with H3 v4 indexing and backend-agnostic interfaces.

## Implementation
 Status

### Currently
 Implemented

- ✅ **geo_infer_space Package**: Main Python package with spatial indexing, analytics, and operations
- ✅ **H3 v4 Migration**: Fully migrated to H3 v4 API
- ✅ **Backend-Agnostic Interfaces**: Unified interfaces supporting multiple backends
- ✅ **Package Metadata**: Generated package metadata (geo_infer_space.egg-info)

## Package
 Structure

### geo_infer_space
/
Main Python package containing:

- **core/**: Core spatial operations (indexing, geometric operations, analytics, unified backend)
- **analytics/**: Spatial analytics and AI-enhanced analysis
- **api/**: REST API interfaces
- **models/**: Data models and configuration schemas
- **utils/**: Utility functions
- **nested/**: Nested spatial operations and messaging

### Key
 Components

- **SpatialIndexingInterface**: H3 v4 spatial indexing with backend-agnostic API
- **SpatialAnalyticsInterface**: AI-enhanced spatial analytics using SRAI
- **GeometricOperationsInterface**: Geometric operations and transformations
- **UnifiedH3Backend**: H3 v4 backend implementation

## Quick
 Start

```python
from geo_infer_space import SpatialIndexingInterface, SpatialAnalyticsInterface
from geo_infer_space.core.dispatcher import configure_backends

# Configure
 backends
configure_backends({
    'default_backends': {
        'indexing': 'h3',
        'analytics': 'srai'
    }})

# Use
 spatial indexing
indexer = SpatialIndexingInterface()
cell = indexer.latlng_to_cell(37.7749, -122.4194, 9)

# Use
 spatial analytics
analytics = SpatialAnalyticsInterface()
hotspots = analytics.analyze_hotspots(spatial_data)```

## Integration

- **Location**: `GEO-INFER-SPACE/src`
- **Purpose**: Source code implementation directory
- **Package**: `geo_infer_space` - Main Python package for spatial operations
- **H3 Version**: v4.0+ (fully migrated)

---

This AGENTS.md documents the source code directory for GEO-INFER-SPACE.
