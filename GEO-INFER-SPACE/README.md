# GEO-INFER-SPACE

**Core Geospatial Engine for Advanced Spatial Methods and Analytics**

## Overview

GEO-INFER-SPACE is the **foundational geospatial processing and analysis engine** within the GEO-INFER framework. It provides a comprehensive suite of advanced spatial methods, algorithms, data structures, and indexing systems for effectively managing, analyzing, and understanding all forms of geospatial data—pertaining to land, water, air, and beyond. This module empowers all other GEO-INFER components with robust capabilities for handling spatial geometries, performing complex spatial operations, conducting real-time analytics, integrating Earth Observation (EO) data, and leveraging diverse coordinate reference systems. Its focus is on providing a high-performance, scalable, and extensible backbone for all explicitly spatial computations across the framework.

## Core Objectives

-   **Provide Comprehensive Spatial Functionality:** Offer a rich set of tools for all common and advanced geospatial operations, from basic geometric calculations to complex spatial modeling.
-   **Enable Efficient Spatial Data Handling:** Implement efficient data structures, spatial indexing, and I/O operations to manage and process large and diverse geospatial datasets (vector, raster, point clouds).
-   **Support Advanced Spatial Analysis & Modeling:** Equip users and other modules with the capabilities to perform sophisticated spatial analytics, pattern detection, and predictive modeling.
-   **FacilitATE Real-time Geospatial Processing:** Provide mechanisms for ingesting, analyzing, and reacting to streaming geospatial data from IoT, sensors, and other real-time sources.
-   **Standardize Earth Observation Data Access:** Simplify the integration and use of EO data through standard protocols like STAC and provide tools for its specialized processing.
-   **Ensure Accurate Coordinate Reference System (CRS) Management:** Handle CRS transformations rigorously to maintain geospatial accuracy and interoperability.
-   **Promote Scalability and Performance:** Design for efficiency and scalability to handle demanding geospatial computations, from local processing to distributed environments.

## Key Features

### 1. Multi-Resolution Spatial Indexing Systems
-   **Description:** A suite of powerful spatial indexing techniques to accelerate spatial queries, neighborhood searches, and data retrieval from large vector and raster datasets.
-   **Systems Implemented/Examples:** H3 Hexagonal Hierarchical Index, QuadTrees, R-Trees, Geohashes, S2 Cells. Each system is optimized for different data types, query patterns, and global/regional coverage needs.
-   **Benefits:** Dramatically improved performance for spatial searches and analyses, efficient handling of massive geospatial datasets, support for multi-resolution data representation and aggregation.

### 2. Real-Time Geospatial Analytics & Edge Computing Support
-   **Description:** Capabilities for processing and analyzing streaming geospatial data from IoT devices, mobile sensors, and other real-time feeds. Includes considerations for edge deployment of spatial algorithms.
-   **Techniques/Examples:** Real-time geofencing, dynamic hotspot detection, trajectory analysis on moving objects, integration with message queues (e.g., Kafka) for data streams. Lightweight spatial functions suitable for edge devices.
-   **Benefits:** Enables timely decision-making based on live spatial information, supports location-based services, facilitates monitoring of dynamic phenomena (e.g., traffic, environmental changes).

### 3. Earth Observation (EO) Data Integration (STAC & COG Support)
-   **Description:** Tools and interfaces for discovering, accessing, and processing EO data from various providers, emphasizing modern cloud-optimized formats and catalogs.
-   **Techniques/Examples:** SpatioTemporal Asset Catalog (STAC) client for searching and retrieving imagery (e.g., Sentinel, Landsat, Planet). Efficient processing of Cloud-Optimized GeoTIFFs (COGs). Common EO data transformations (e.g., atmospheric correction components, spectral index calculation like NDVI, EVI).
-   **Benefits:** Streamlined access to vast archives of satellite and aerial imagery, efficient processing of large EO datasets, support for time-series analysis of environmental changes.

### 4. Advanced Spatial Operations and Algorithms
-   **Description:** A rich library of algorithms for performing complex spatial analysis, modeling, and data manipulation on both vector and raster data.
-   **Techniques/Examples:**
    -   **Vector:** Advanced overlay analysis, network analysis (routing, service areas), topology correction, generalization, 3D spatial operations.
    -   **Raster:** Map algebra, terrain analysis (slope, aspect, viewshed, watersheds), image segmentation, texture analysis, focal/zonal statistics.
    -   **Point Cloud:** Processing (filtering, classification), feature extraction from LiDAR or photogrammetric point clouds.
-   **Benefits:** Enables sophisticated understanding of spatial relationships, patterns, and processes across diverse application domains.

### 5. Robust Coordinate Reference System (CRS) Management
-   **Description:** Rigorous handling of projections and transformations between different geographic and projected coordinate systems to ensure data accuracy and interoperability.
-   **Techniques/Examples:** Utilizes underlying libraries like PROJ, supports EPSG code lookups, on-the-fly reprojection for analysis and visualization, handling of vertical datums.
-   **Benefits:** Prevents common errors related to mismatched CRSs, ensures all spatial data is accurately georeferenced and aligned for analysis.

### 6. OS Climate Integration for Standardized Geospatial Processing
- **Description:** Integration with selected tools and services from the OS-Climate initiative, particularly those related to H3 grid services and data loading, promoting standardization in climate-related geospatial analysis. We use forks of these repositories under github.com/docxology, originally from github.com/os-climate.

## Success Story: Cascadian Agricultural Land Analysis Framework

**GEO-INFER-SPACE has powered the production-ready Cascadian Agricultural Land Analysis Framework**, demonstrating the effectiveness of centralized geospatial utilities.

### Integration Achievements

**100% Test Coverage Success**: The Cascadian framework achieved complete test coverage (9/9 tests passing) through SPACE integration.

**Production-Ready Features Enabled**:
- **H3 Spatial Indexing**: H3 hexagonal grid processing across 30,021+ hexagons
- **OSC Repository Integration**: Integration with OS-Climate tools for standardized operations
- **Cross-Border Analysis**: California + Oregon data integration
- **Real-Time Processing**: API integration with government data sources
- **Interactive Visualization**: Multi-layer dashboards with spatial analysis

### Technical Implementation

**Centralized Utilities Success**:
```python
# All Cascadian modules use SPACE utilities
from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng, polygon_to_cells
from geo_infer_space.core.spatial_processor import SpatialProcessor
from geo_infer_space.osc_geo import create_h3_data_loader
```

**Key Performance Metrics**:
- **30,021 H3 hexagons** processed efficiently
- **4 production modules** (Zoning, Current Use, Ownership, Improvements)
- **Multiple export formats** (GeoJSON, CSV, JSON, HTML)
- **Real-time API integration** with fallback mechanisms
- **Spatial analysis** including correlation and hotspot detection

### Framework Benefits

1. **Consistency**: Unified H3 operations across all modules
2. **Maintainability**: Centralized geospatial logic reduces duplication
3. **Scalability**: Efficient processing of large spatial datasets
4. **Interoperability**: Cross-module data integration
5. **Quality**: Robust error handling and data validation

**Location**: [`GEO-INFER-PLACE/locations/cascadia/`](../GEO-INFER-PLACE/locations/cascadia/)  
**Documentation**: Technical framework with API reference  
**Status**: Production ready with test coverage

This demonstrates SPACE's capability to support real-world geospatial analysis frameworks with production-quality results.

## Data Flow

### Inputs
- **Primary Data Sources**:
  - Vector data (GeoJSON, Shapefile, GeoPackage) from GEO-INFER-DATA
  - Raster data (GeoTIFF, NetCDF, COG) from Earth observation archives
  - Real-time sensor streams via GEO-INFER-TIME
  - Point cloud data (LAS/LAZ files) for 3D analysis
  - Network data (road networks, utilities) for connectivity analysis

- **Configuration Requirements**:
  - `spatial_config.yaml`: CRS definitions, indexing parameters
  - Environment variables: GDAL_DATA, PROJ_LIB paths
  - Database connections: PostGIS connection strings

- **Dependencies**:
  - **Required**: GEO-INFER-DATA (data storage), GEO-INFER-MATH (calculations)
  - **Optional**: GEO-INFER-TIME (temporal analysis), GEO-INFER-AI (ML features)

### Processes
- **Core Spatial Operations**:
  - Geometric calculations (area, perimeter, distance)
  - Spatial relationships (intersects, contains, overlaps)
  - Coordinate reference system transformations
  - Spatial indexing (H3, QuadTree, R-Tree) for performance optimization

- **Analytical Methods**:
  - Buffer analysis and proximity calculations
  - Overlay operations (union, intersection, difference)
  - Network analysis (shortest path, service areas)
  - Raster analysis (map algebra, terrain analysis, focal statistics)

- **Transformation Steps**:
  1. Data validation and CRS harmonization
  2. Spatial indexing for query optimization
  3. Geometric processing and analysis
  4. Result aggregation and output formatting

### Outputs
- **Data Products**:
  - Processed spatial datasets (vector/raster)
  - Spatial analysis results (statistics, measurements)
  - Derived spatial features (buffers, centroids, boundaries)
  - Spatial indices and optimized data structures

- **Visualization**:
  - Interactive maps via GEO-INFER-APP
  - Spatial analysis visualizations (heat maps, choropleth maps)
  - 3D visualizations for elevation and point cloud data

- **Integration Points**:
  - Spatial features for GEO-INFER-AI model training
  - Processed geometries for GEO-INFER-SIM simulations
  - Analysis results for GEO-INFER-HEALTH accessibility studies
  - Optimized spatial queries for all domain-specific modules

## Module Architecture (Conceptual)

```mermaid
graph TD
    subgraph SPACE_Core as "GEO-INFER-SPACE Core Engine"
        API_SPACE[API Layer (FastAPI, GeoServer Adapters)]
        SERVICE_SPACE[Service Layer (Orchestration, Workflow Management)]
        ANALYTICS_ENGINE[Spatial Analytics Engine]
        INDEXING_SUBSYS[Spatial Indexing Subsystem]
        CRS_MANAGER[CRS Management Subsystem]
        IO_HANDLER[Data I/O & Format Handler]
    end

    subgraph Analytics_Components as "Analytical Algorithm Libraries"
        VECTOR_OPS[Vector Operations Library (Shapely, GEOS based)]
        RASTER_OPS[Raster Operations Library (Rasterio, GDAL based)]
        POINT_CLOUD_OPS[Point Cloud Processing Library (e.g., PDAL wrapper)]
        NETWORK_ANALYST[Network Analysis Tools (e.g., NetworkX, igraph based)]
        GEOSTAT_TOOLS[Geostatistics & Interpolation Tools]
    end

    subgraph Data_Access_Integration as "Data Access & External Integrations"
        DATA_MOD_GI[GEO-INFER-DATA (Primary Data Source)]
        STAC_CLIENT[STAC Client for EO Data]
        OSC_GEO_INT[OS-Climate H3 Tools Integration]
        REALTIME_INGEST[Real-time Data Ingestion Points (Kafka, MQTT)]
        DB_SPATIAL[(Spatial Databases - PostGIS, etc.)]
    end

    %% Core Engine Connections
    API_SPACE --> SERVICE_SPACE
    SERVICE_SPACE --> ANALYTICS_ENGINE; SERVICE_SPACE --> INDEXING_SUBSYS; SERVICE_SPACE --> CRS_MANAGER; SERVICE_SPACE --> IO_HANDLER

    %% Analytics Engine uses Algorithm Libraries
    ANALYTICS_ENGINE --> VECTOR_OPS; ANALYTICS_ENGINE --> RASTER_OPS; ANALYTICS_ENGINE --> POINT_CLOUD_OPS; ANALYTICS_ENGINE --> NETWORK_ANALYST; ANALYTICS_ENGINE --> GEOSTAT_TOOLS

    %% IO Handler interacts with Data Access/Integration components
    IO_HANDLER --> DATA_MOD_GI; IO_HANDLER --> STAC_CLIENT; IO_HANDLER --> OSC_GEO_INT; IO_HANDLER --> REALTIME_INGEST; IO_HANDLER --> DB_SPATIAL

    %% Indexing and CRS support Analytics and I/O
    INDEXING_SUBSYS --> ANALYTICS_ENGINE; INDEXING_SUBSYS --> IO_HANDLER
    CRS_MANAGER --> ANALYTICS_ENGINE; CRS_MANAGER --> IO_HANDLER

    %% Algorithms use Math
    VECTOR_OPS --> MATH_MOD_GI[GEO-INFER-MATH]
    RASTER_OPS --> MATH_MOD_GI
    GEOSTAT_TOOLS --> MATH_MOD_GI
    NETWORK_ANALYST --> MATH_MOD_GI

    classDef spacemodule fill:#e0f7fa,stroke:#00796b,stroke-width:2px;
    class SPACE_Core,Analytics_Components spacemodule;
```

-   **Core Engine:** Provides APIs, orchestrates spatial workflows, and manages the core subsystems.
-   **Analytical Algorithm Libraries:** Contains implementations of various vector, raster, point cloud, and network analysis algorithms, often leveraging `GEO-INFER-MATH`.
-   **Subsystems:** Dedicated components for spatial indexing, CRS management, and data I/O.
-   **Data Access & Integration:** Interfaces with `GEO-INFER-DATA`, external EO catalogs (STAC), OS-Climate tools, real-time data streams, and spatial databases.

## Integration with other GEO-INFER Modules

GEO-INFER-SPACE is a critical enabling module for most other parts of the framework:

-   **GEO-INFER-DATA:** SPACE relies on DATA for the provision and storage of various geospatial datasets. In turn, SPACE may perform transformations or generate new spatial layers that are managed by DATA.
-   **GEO-INFER-TIME:** When combined with TIME, SPACE enables powerful spatio-temporal analysis, tracking changes in spatial phenomena over time or analyzing moving objects.
-   **GEO-INFER-MATH:** Provides the fundamental mathematical algorithms (geometry, linear algebra, statistics) that underpin many of the spatial operations within SPACE.
-   **GEO-INFER-AI & GEO-INFER-AGENT:** SPACE provides the spatial context, features (e.g., proximity, density), and environmental representations for AI models and intelligent agents. For instance, agents in a simulation (via AGENT and SIM) navigate and interact within a spatial environment defined and managed by SPACE.
-   **GEO-INFER-SIM:** Simulations of spatial processes (urban growth, disease spread, hydrological models) require SPACE for representing the geographic environment, performing spatial calculations (e.g., distance, visibility), and updating spatial states.
-   **GEO-INFER-APP & GEO-INFER-ART:** SPACE provides the processed and analyzed geospatial data that is then visualized by APP (maps, dashboards) or used as input for ART (geospatial art generation).
-   **Domain-Specific Modules (AG, ECON, HEALTH, RISK, LOG, etc.):** All these modules heavily rely on SPACE for their core spatial data processing and analytical needs (e.g., field delineation in AG, market area analysis in ECON, accessibility in HEALTH, hazard zone mapping in RISK).

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites Check
```bash
# Verify Python version
python --version  # Should be 3.9+

# Check required GEO-INFER modules
pip list | grep geo-infer
```

### 2. Installation
```bash
# Install this module with core dependencies
uv pip install -e ./GEO-INFER-SPACE

# Or install with all optional features
uv pip install -e "./GEO-INFER-SPACE[all]"

# Verify installation
python -c "import geo_infer_space; print('✅ Installation successful')"
```

### 3. Basic Configuration
```bash
# Copy example configuration
cp config/example.yaml config/local.yaml

# Edit with your settings (minimal required changes marked with TODO)
nano config/local.yaml
```

### 4. Run First Example
```python
# Vector operations example
import geopandas as gpd
from shapely.geometry import Point
from geo_infer_space.analytics.vector import buffer_and_intersect, geometric_calculations

# Create sample data
points = gpd.GeoDataFrame(
    geometry=[Point(-122.4, 37.77), Point(-122.3, 37.78)], 
    crs="EPSG:4326"
)
polygons = gpd.GeoDataFrame(
    geometry=[Point(-122.35, 37.775).buffer(0.01)], 
    crs="EPSG:4326"
)

# Project to metric CRS and perform buffer analysis
points_proj = points.to_crs("EPSG:3857")
polygons_proj = polygons.to_crs("EPSG:3857")
result = buffer_and_intersect(points_proj, polygons_proj, 1000)  # 1km buffer

print(f"Buffer analysis result: {len(result)} features")

# Calculate geometric properties
props = geometric_calculations(polygons)
print(f"Polygon area: {props['area'].iloc[0]:.6f} square degrees")
```

### 5. H3 Hexagonal Grid Example
```python
# H3 operations example
from geo_infer_space.utils.h3_utils import latlng_to_cell, polygon_to_cells

# Convert coordinates to H3 cell
cell = latlng_to_cell(37.7749, -122.4194, resolution=9)
print(f"H3 cell: {cell}")

# Convert polygon to H3 cells
polygon = {
    "type": "Polygon",
    "coordinates": [[
        [-122.42, 37.77], [-122.41, 37.77],
        [-122.41, 37.78], [-122.42, 37.78],
        [-122.42, 37.77]
    ]]
}
cells = polygon_to_cells(polygon, resolution=9)
print(f"Polygon covers {len(cells)} H3 cells")
```

### 6. REST API Example
```python
# Start the API server
from geo_infer_space.api import app
import uvicorn

# Run server (in production, use proper WSGI server)
uvicorn.run(app, host="0.0.0.0", port=8000)

# In another terminal, test the API
import requests
import json

# Test buffer analysis endpoint
data = {
    "data": {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-122.4, 37.77]},
            "properties": {}
        }]
    },
    "buffer_distance": 1000,
    "crs": "EPSG:3857"
}

response = requests.post("http://localhost:8000/api/v1/buffer", json=data)
print(f"API response: {response.status_code}")
```

### 7. Next Steps
- 📖 See [detailed examples](./examples/) for advanced usage
- 🔗 Check [API documentation](http://localhost:8000/docs) when server is running
- 🛠️ Visit [configuration reference](./docs/configuration.md) for all options
- 🧪 Run tests: `pytest tests/ -v`

## Getting Started (Detailed)

### Prerequisites
-   Python 3.9+
-   Core GEO-INFER framework installed.
-   Essential geospatial libraries: GDAL (usually a system dependency), Rasterio, GeoPandas, Shapely, PyPROJ.
-   For specific features: `pystac_client`, H3 Python bindings, libraries for point cloud processing (e.g., `pdal`).

### Installation
```bash
# Ensure the main GEO-INFER repository is cloned
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER

pip install -e ./GEO-INFER-SPACE
# Or if managed by a broader project build system.
```
### CLI Tools

After installation, the following console commands are available to support H3 migration and checks:

```bash
# Verify H3 v4 compliance across the repo
gis-verify-h3-v4

# Migrate legacy H3 v3 calls to v4 API
gis-fix-h3-v4

# Quick fix helpers
gis-fix-h3-calls
gis-fix-double-h3
gis-fix-imports
gis-fix-rel-imports

# Run simple H3 verification tests
gis-h3-tests
```

These tools live under `src/geo_infer_space/tools/` and can be called from any working directory within the repo.


### Configuration
Configuration for GEO-INFER-SPACE might include:
-   Default CRS for new projects.
-   Paths to external tools or libraries (if not fully bundled).
-   API keys for EO data services or commercial data providers.
-   Parameters for spatial indexing defaults.
-   Configuration for OS-Climate tool integration (see `README-OSC.md`).
These are typically managed in YAML files (e.g., `GEO-INFER-SPACE/config/space_config.yaml`).

### Basic Usage Examples (Illustrative)

**1. Buffer Analysis & Intersection (Vector Operations)**
```python
import geopandas as gpd
from geo_infer_space.analytics.vector import buffer_and_intersect

points_gdf = gpd.read_file("path/to/points_of_interest.geojson")
polygons_gdf = gpd.read_file("path/to/study_areas.geojson")

# Buffer points by 500 meters and find intersections with study areas
result_gdf = buffer_and_intersect(points_gdf, polygons_gdf, buffer_distance_meters=500)
result_gdf.to_file("outputs/buffered_intersections.geojson")
```

**2. Raster Terrain Analysis (Slope Calculation)**
```python
import rasterio
# from geo_infer_space.analytics import calculate_slope # Conceptual

# dem_path = "path/to/digital_elevation_model.tif"
# # slope_raster_path = "outputs/slope_map.tif"
# # calculate_slope(input_dem_path=dem_path, output_slope_path=slope_raster_path)

# with rasterio.open(dem_path) as src:
#     print(f"DEM Resolution: {src.res}")
```

**3. Using H3 Indexing (v4)**
```python
from geo_infer_space.utils.h3_utils import latlng_to_cell, cell_to_latlng_boundary

cell = latlng_to_cell(40.7128, -74.0060, 9)
boundary = cell_to_latlng_boundary(cell)
```

**4. OS Climate H3 Grid Service Usage (from existing README)**
```python
# from geo_infer_space.osc_geo import create_h3_grid_manager, load_data_to_h3_grid
# grid_manager = create_h3_grid_manager(auto_start=True)
# load_data_to_h3_grid(
# input_file="data/example.geojson",
# output_file="output/h3_data.geojson",
# resolution=8
# )
```

## 🔧 Comprehensive Spatial Analytics Capabilities

### Vector Operations
- **Buffer Analysis**: Create buffers around geometries with distance-based analysis
- **Overlay Operations**: Union, intersection, difference, symmetric difference
- **Proximity Analysis**: Nearest neighbor searches, distance matrices, spatial relationships
- **Spatial Joins**: Attribute-based spatial relationships (intersects, contains, within, etc.)
- **Geometric Calculations**: Area, perimeter, centroid, compactness, convex hull properties
- **Topology Operations**: Simplification, buffering, convex hull, envelope, dissolve

### Raster Analysis
- **Terrain Analysis**: Slope, aspect, hillshade, curvature, topographic position index (TPI)
- **Map Algebra**: Mathematical operations on raster layers with custom expressions
- **Focal Statistics**: Moving window operations (mean, sum, std, min, max, median)
- **Zonal Statistics**: Statistical summaries within polygon zones
- **Raster Overlay**: Multi-layer combination with various methods (sum, mean, weighted)
- **Image Processing**: Gaussian filtering, median filtering, edge detection, histogram equalization

### Network Analysis
- **Shortest Path**: Optimal routing between points with customizable weights
- **Service Areas**: Isochrone/isodistance analysis from center points
- **Network Connectivity**: Graph metrics, component analysis, centrality measures
- **Routing Analysis**: Origin-destination matrices for multiple points
- **Accessibility Analysis**: Reachability and accessibility metrics

### Geostatistics
- **Spatial Interpolation**: IDW, Kriging, RBF, nearest neighbor methods
- **Clustering Analysis**: DBSCAN, K-means, hierarchical clustering
- **Hotspot Detection**: Getis-Ord Gi*, Local Moran's I, kernel density estimation
- **Spatial Autocorrelation**: Global Moran's I, Geary's C statistics
- **Variogram Analysis**: Experimental variogram calculation and modeling

### H3 Hexagonal Grid Operations
- **Coordinate Conversion**: Lat/lng to H3 cells and vice versa
- **Polygon Coverage**: Convert polygons to H3 cell sets
- **Grid Operations**: K-ring neighborhoods, grid distances, compaction
- **Boundary Calculation**: H3 cell boundary extraction
- **Multi-resolution**: Support for all H3 resolutions (0-15)

### Point Cloud Processing
- **Data Loading**: Support for LAS/LAZ, CSV, text formats
- **Filtering**: Statistical outlier removal, radius filtering, voxel grid downsampling
- **Feature Extraction**: Geometric features from point neighborhoods
- **Classification**: Ground/vegetation/building detection, clustering-based classification
- **Surface Generation**: Triangulation, grid interpolation, contour generation

### Data I/O Capabilities
- **Vector Formats**: GeoJSON, Shapefile, GeoPackage, KML, CSV, Excel, Parquet, Feather
- **Raster Formats**: GeoTIFF, COG, NetCDF, various image formats
- **Point Cloud Formats**: LAS/LAZ files, text-based formats
- **Streaming**: Support for large datasets with chunked processing
- **Format Detection**: Automatic format detection and validation

### REST API Endpoints
- **`/api/v1/buffer`**: Buffer analysis operations
- **`/api/v1/proximity`**: Proximity and distance analysis
- **`/api/v1/interpolation`**: Spatial interpolation services
- **`/api/v1/clustering`**: Spatial clustering analysis
- **`/api/v1/hotspots`**: Hotspot detection services
- **`/api/v1/network`**: Network analysis operations
- **`/api/v1/h3`**: H3 hexagonal grid operations
- **`/api/v1/health`**: Service health monitoring
- **`/api/v1/capabilities`**: Available analysis capabilities

### Performance Features
- **Parallel Processing**: Multi-core support for computationally intensive operations
- **Spatial Indexing**: R-tree, QuadTree, H3, Geohash indexing for fast queries
- **Caching**: Redis and in-memory caching for repeated operations
- **Streaming**: Memory-efficient processing of large datasets
- **Optimization**: NumPy/SciPy optimized algorithms, optional Numba JIT compilation

## Performance and Scaling Strategies

-   **Efficient Algorithms & Data Structures:** Use of optimized algorithms and appropriate data structures (e.g., R-trees by GeoPandas/Shapely).
-   **Spatial Indexing:** As mentioned, critical for fast queries on large datasets.
-   **Parallel Processing:** Leveraging multi-core CPUs for operations that can be parallelized (e.g., using Dask with GeoPandas, or custom parallelism for raster tiling).
-   **GPU Acceleration:** For certain raster operations or machine learning components involving spatial data, potentially via libraries like CuPy or RAPIDS cuSpatial.
-   **Cloud-Optimized Formats:** Prioritizing COGs and other cloud-friendly formats to enable efficient partial reads and streaming.
-   **Distributed Computing Frameworks:** For very large-scale tasks, integration points for frameworks like Apache Spark (with GeoSpark/Apache Sedona) or Dask can be considered.
-   **Edge Computing:** Designing lightweight spatial functions for deployment on edge devices to process data closer to the source.

## Directory Structure
```
GEO-INFER-SPACE/
├── bin/                    # Executable scripts (e.g., for OS-Climate tools if needed locally)
├── config/                 # Configuration files (CRS defaults, API keys, indexing params)
├── docs/                   # Detailed documentation, algorithm descriptions, tutorials
│   └── osc_geo/            # Specific docs for OS-Climate integration (if not in main README-OSC.md)
├── examples/               # Example scripts and notebooks for various spatial operations
├── repo/                   # Cloned OS Climate repositories
├── reports/                # Generated reports from analyses or OS-Climate tools
├── repos/                  # Other external repositories, if any (mirroring current structure)
├── src/
│   └── geo_infer_space/
│       ├── __init__.py
│       ├── api/            # API endpoints for spatial services
│       ├── analytics/      # Core spatial analysis algorithms (vector, raster, network, geostat)
│       ├── core/           # Fundamental spatial object representations, core logic
│       ├── indexing/       # Spatial indexing implementations (H3, RTree wrappers, etc.)
│       ├── io/             # Data input/output handlers (GeoJSON, Shapefile, GeoTIFF, STAC)
│       ├── models/         # Pydantic models for spatial data structures/requests
│       ├── osc_geo/        # OS Climate integration module (as existing)
│       └── utils/          # Utility functions (CRS helpers, geometry validation)
│       └── geo_infer_space.egg-info/ # Packaging info
├── tests/
│   └── osc_geo/            # Tests for OS-Climate integration
├── venv/                   # Virtual environment (typically in .gitignore)
└── docs/README-OSC.md      # OS Climate integration details (as existing)
```

## Future Development

-   Enhanced support for 3D geospatial data and analytics (e.g., CityGML, 3D tiles, volumetric analysis).
-   Advanced point cloud processing capabilities directly within the module.
-   Tighter integration with distributed computing frameworks for massive datasets.
-   Development of a more comprehensive spatial web services API (OGC compliant where appropriate).
-   Expansion of real-time and streaming analytics features, including complex event processing on spatial streams.
-   AI-driven spatial feature extraction and pattern recognition.

## Contributing

Contributions to GEO-INFER-SPACE are highly valued. This can include implementing new spatial algorithms, optimizing existing ones, improving support for data formats or CRSs, enhancing real-time capabilities, adding more examples, or improving documentation. Please follow the main `CONTRIBUTING.md` in the GEO-INFER root directory and any specific guidelines in `GEO-INFER-SPACE/docs/CONTRIBUTING_SPACE.md` (to be created).

## License

This module, as part of the GEO-INFER framework, is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 

## Role in GEO-INFER Framework

GEO-INFER-SPACE serves as the central repository for **all general spatial methods**, **H3 indexing operations**, **OSC (OS-Climate) integration methods**, and **core data integration aspects**. This module provides the foundational geospatial capabilities that other modules, such as GEO-INFER-PLACE, depend on. Place-specific modules like PLACE should focus exclusively on location-oriented logic and import general spatial functionality from SPACE to ensure modularity, reusability, and adherence to framework principles.

Key Assertions:
- **Spatial Methods**: All vector, raster, point cloud, and network operations are implemented here.
- **H3 and Indexing**: Comprehensive H3 utilities, polygon_to_cells, boundary calculations, and other indexing systems.
- **OSC Integration**: Cloning, management, and usage of OS-Climate repositories for standardized geospatial processing.
- **Data Integration**: General data loading, transformation, and integration logic for geospatial data sources.

Modules like GEO-INFER-PLACE must not duplicate these functionalities and should import from SPACE for all general spatial needs. 