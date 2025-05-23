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
-   **Description:** Integration with selected tools and services from the OS-Climate initiative, particularly those related to H3 grid services and data loading, promoting standardization in climate-related geospatial analysis.
-   **Components:** Wrappers or direct usage of `osc-geo-h3grid-srv` for H3 grid generation/management and `osc-geo-h3loader-cli` for loading data into H3 grids.
-   **Benefits:** Facilitates interoperability with OS-Climate workflows, leverages standardized H3-based approaches for climate data, promotes collaboration within the climate finance and science community.

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

## Getting Started

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
# from geo_infer_space.analytics import buffer_and_intersect # Conceptual

# points_gdf = gpd.read_file("path/to/points_of_interest.geojson")
# polygons_gdf = gpd.read_file("path/to/study_areas.geojson")

# # Buffer points by 500 meters and find intersections with study areas
# # result_gdf = buffer_and_intersect(points_gdf, polygons_gdf, buffer_distance_meters=500)
# # result_gdf.to_file("outputs/buffered_intersections.geojson")
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

**3. Using H3 Indexing**
```python
import h3
# from geo_infer_space.indexing import points_to_h3 # Conceptual

# point_lat, point_lon = 40.7128, -74.0060 # New York City
# h3_resolution = 9
# h3_cell = h3.geo_to_h3(point_lat, point_lon, h3_resolution)
# print(f"H3 Cell for NYC (Res {h3_resolution}): {h3_cell}")

# h3_cell_boundary = h3.h3_to_geo_boundary(h3_cell, geo_json=True)
# print(f"H3 Cell Boundary (GeoJSON): {h3_cell_boundary}")
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

## Spatial Analytics Capabilities (Examples)

-   **Proximity Analysis:** Buffering, nearest neighbor searches, distance matrices.
-   **Overlay Analysis:** Union, intersection, difference, symmetrical difference for vector layers; raster overlay operations.
-   **Network Analysis:** Shortest path, service area calculation, origin-destination cost matrices, traveling salesperson problems.
-   **Terrain Analysis:** Slope, aspect, hillshade, curvature, viewshed analysis, watershed delineation.
-   **Spatial Interpolation:** IDW, kriging, spline interpolation for creating continuous surfaces from point data.
-   **Clustering & Hotspot Detection:** DBSCAN, K-Means (spatial variants), Getis-Ord Gi*, Anselin Local Moran's I.
-   **Raster Processing:** Map algebra, resampling, reclassification, zonal statistics, image filtering.
-   **Geocoding & Reverse Geocoding:** Converting addresses to coordinates and vice-versa (often via external services integrated here).

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
├── ext/os-climate/         # Cloned OS Climate repositories (as per current structure)
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
├── osc_setup_all.py        # Script for OS-Climate setup (as existing)
├── osc_status.py           # Script for OS-Climate status (as existing)
├── osc_wrapper.py          # Wrapper script (as existing)
└── README-OSC.md           # OS Climate integration details (as existing)
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