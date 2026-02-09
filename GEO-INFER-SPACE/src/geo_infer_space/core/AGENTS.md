# Agent: core

## Scope
This agent handles core spatial intelligence components for GEO-INFER-SPACE implementing spatial indexing, analytics, geometric operations, backend management, and data integration.

## Implementation Status

### Currently Implemented

- ✅ **SpatialIndexingInterface**: H3 v4 spatial indexing with backend-agnostic API
- ✅ **SpatialAnalyticsInterface**: AI-enhanced spatial analytics using SRAI
- ✅ **GeometricOperationsInterface**: Geometric operations and transformations
- ✅ **SpatialBackendDispatcher**: Multi-backend dispatcher for spatial operations
- ✅ **UnifiedH3Backend**: Unified H3 backend for comprehensive analysis
- ✅ **SpatialProcessor**: Core spatial processing engine
- ✅ **SpatialStatistics**: Spatial statistics (Moran's I, Getis-Ord G*, etc.)
- ✅ **BaseAnalysisModule**: Base class for analysis modules
- ✅ **DataIntegrator**: Multi-source data integration
- ✅ **PlaceAnalyzer**: Place-based geospatial intelligence

## Agent Capabilities

### 1. Spatial Indexing

```python
from geo_infer_space.core import SpatialIndexingInterface

# Initialize spatial indexer
indexer = SpatialIndexingInterface()

# Convert lat/lng to H3 cell (v4 API)
cell = indexer.latlng_to_cell(37.7749, -122.4194, resolution=9)

# Convert cell to lat/lng
lat, lng = indexer.cell_to_latlng(cell)

# Convert polygon to cells
cells = indexer.polygon_to_cells(polygon, resolution=9)

# Get cell neighbors
neighbors = indexer.get_cell_neighbors(cell, k=1)```

### 2. Spatial Analytics

```python
from geo_infer_space.core import SpatialAnalyticsInterface

# Initialize analytics
analytics = SpatialAnalyticsInterface()

# Analyze hotspots
hotspots = analytics.analyze_hotspots(spatial_data)

# Compute proximity
proximity = analytics.compute_proximity(points)

# Cluster points
clusters = analytics.cluster_points(points)

# Detect patterns
patterns = analytics.detect_patterns(data)```

### 3. Geometric Operations

```python
from geo_infer_space.core import GeometricOperationsInterface

# Initialize geometric operations
geom_ops = GeometricOperationsInterface()

# Buffer geometry
buffered = geom_ops.buffer_geometry(geometry, distance=1000)

# Calculate area
area = geom_ops.calculate_area(geometry)

# Calculate distance
distance = geom_ops.calculate_distance(geom1, geom2)

# Transform CRS
transformed = geom_ops.transform_geometry(geometry, from_crs='EPSG:4326', to_crs='EPSG:3857')```

### 4. Backend Management

```python
from geo_infer_space.core.dispatcher import SpatialBackendDispatcher, configure_backends

# Configure backends
configure_backends({
    'default_backends': {
        'indexing': 'h3',
        'analytics': 'srai'
    }})

# Get dispatcher
dispatcher = get_backend_dispatcher()

# Register custom backend
dispatcher.register_backend('custom', custom_backend)

# Dispatch operations
result = dispatcher.dispatch_indexing_operation('latlng_to_cell', 37.7749, -122.4194, 9)```

### 5. Spatial Statistics

```python
from geo_infer_space.core import SpatialStatistics

# Initialize statistics
stats = SpatialStatistics()

# Calculate Moran's I
moran_result = stats.moran_i(cells, values, weight_type='queen')

# Calculate Getis-Ord G*
getis_result = stats.getis_ord_g(cells, values, distance=3)

# Nearest neighbor analysis
nn_result = stats.nearest_neighbor_index(cells)```

## Key Classes

### SpatialIndexingInterface
Generic interface for spatial indexing operations using H3 v4.

**Key Methods**:
- `latlng_to_cell(lat, lng, resolution) -> str`
- `cell_to_latlng(cell) -> tuple[float, float]`
- `polygon_to_cells(polygon, resolution) -> List[str]`
- `get_cell_neighbors(cell, k) -> List[str]`
- `get_cell_distance(cell1, cell2) -> int`

### SpatialAnalyticsInterface
Generic interface for spatial analytics operations.

**Key Methods**:
- `analyze_hotspots(data) -> Dict[str, Any]`
- `compute_proximity(points) -> Dict[str, Any]`
- `cluster_points(points) -> Dict[str, Any]`
- `detect_patterns(data) -> Dict[str, Any]`
- `analyze_accessibility(origins, destinations) -> Dict[str, Any]`

### GeometricOperationsInterface
Generic interface for geometric operations.

**Key Methods**:
- `buffer_geometry(geometry, distance) -> Dict[str, Any]`
- `calculate_area(geometry) -> float`
- `calculate_distance(geom1, geom2) -> float`
- `transform_geometry(geometry, from_crs, to_crs) -> Dict[str, Any]`
- `union_geometries(geometries) -> Dict[str, Any]`

### SpatialBackendDispatcher
Central dispatcher for spatial operations across different backends.

**Key Methods**:
- `register_backend(name, backend) -> None`
- `get_backend(name) -> Optional[SpatialBackendInterface]`
- `dispatch_indexing_operation(operation, *args, **kwargs) -> Any`
- `dispatch_analytics_operation(operation, *args, **kwargs) -> Any`

### UnifiedH3Backend
Unified H3-indexed backend for comprehensive geospatial analysis.

**Key Methods**:
- `run_comprehensive_analysis() -> None`
- `calculate_analysis_scores() -> Dict[str, Dict]`
- `export_unified_data(output_path, format) -> None`
- `generate_interactive_dashboard(output_path) -> None`

## Integration

- **Location**: `GEO-INFER-SPACE/src/geo_infer_space/core`
- **Dependencies**: `h3`, `srai`, `geopandas`, `shapely`
- **Used By**: Analytics, API, nested operations modules
- **Provides**: Core spatial operations for the GEO-INFER framework

---

This AGENTS.md documents core spatial intelligence components for GEO-INFER-SPACE.
