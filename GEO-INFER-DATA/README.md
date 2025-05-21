# GEO-INFER-DATA

**Geospatial Data Management, ETL, and Storage Optimization**

## Overview

GEO-INFER-DATA serves as the **foundational data backbone** for the entire GEO-INFER framework. It is responsible for the systematic management of diverse geospatial datasets, implementing robust Extract, Transform, Load (ETL) pipelines, and optimizing data storage and access. This module ensures that all other GEO-INFER components have reliable, timely, and efficient access to high-quality, analysis-ready geospatial data. It addresses challenges related to data heterogeneity, volume, velocity, and veracity, providing a cohesive data layer that supports complex geospatial inference, modeling, and application development.

## Core Objectives

-   **Data Accessibility:** Provide unified and efficient access to a wide variety of geospatial data sources.
-   **Data Quality:** Implement rigorous validation, cleaning, and quality assurance processes.
-   **Interoperability:** Support common geospatial data formats and standards to facilitate data exchange.
-   **Scalability:** Design storage and processing solutions that can scale with growing data volumes and user demands.
-   **Efficiency:** Optimize data pipelines and storage for rapid data retrieval and analysis.
-   **Governance:** Establish clear protocols for data lineage, versioning, metadata management, and access control.

## Key Features

-   **Distributed Geospatial Data Warehousing:** Design and management of data lake and data warehouse architectures suitable for large-scale geospatial data, enabling efficient querying and analytics across diverse datasets.
    -   Integration with PostGIS, MinIO, TimescaleDB, and other specialized data stores.
-   **Intelligent ETL (Extract, Transform, Load) Pipelines:** Configurable and automatable pipelines for ingesting data from various sources (files, APIs, databases, streams), transforming it into analysis-ready formats (e.g., projection, cleaning, feature engineering), and loading it into the data warehouse or designated storage.
    -   Support for batch and stream processing.
-   **Version Control for Geospatial Datasets:** Mechanisms for tracking changes to datasets over time, enabling reproducibility, rollback capabilities, and collaborative data management (e.g., leveraging DVC - Data Version Control, or custom solutions integrated with Git).
-   **Data Quality Assurance & Validation Workflows:** Automated and manual processes for assessing data accuracy, completeness, consistency, and timeliness. Includes tools for defining validation rules and generating quality reports.
-   **Metadata Management & Cataloging:** Systems for capturing, storing, and querying metadata about datasets (e.g., source, lineage, schema, spatial/temporal extent, quality). Adherence to standards like ISO 19115, SpatioTemporal Asset Catalogs (STAC).
-   **Data API & Access Services:** Provides standardized APIs (e.g., RESTful, OGC WFS/WCS/WMS) for other modules and applications to discover, query, and retrieve geospatial data.
-   **Geospatial Data Indexing:** Advanced spatial and temporal indexing strategies (e.g., R-trees, Quadtrees, H3, space-filling curves) to accelerate queries and analytical operations.

## Data Flow & ETL Architecture (Conceptual)

```mermaid
graph TD
    subgraph Data_Sources as "Data Sources"
        FILES[Files (GeoJSON, Shapefile, GeoTIFF)]
        DATABASES[Databases (PostgreSQL, External DBs)]
        APIS[APIs (STAC, OGC, Custom)]
        STREAMS[Real-time Streams (Sensors, IoT)]
    end

    subgraph ETL_Pipeline as "GEO-INFER-DATA ETL Engine"
        EXTRACT[Extract Layer]
        TRANSFORM[Transform Layer]
        LOAD[Load Layer]
        VALIDATE[Validation & QA]
        METADATA[Metadata Management]
        VERSIONING[Data Versioning]
    end

    subgraph Data_Storage_Access as "Data Storage & Access Layer"
        WAREHOUSE[Geospatial Data Warehouse]
        DB_POSTGIS[PostGIS (Vector)]
        DB_TIMESERIES[TimescaleDB (Time-Series)]
        OBJECT_STORE[Object Storage (MinIO/S3 - Raster, Files)]
        CACHE[Cache (Redis)]
        DATA_API[Data Access API]
    end

    subgraph Data_Consumers as "Data Consumers"
        ANALYSIS_MOD[Analysis Modules (SPACE, TIME, AI, ACT)]
        APP_MOD[Application Modules (APP, ART)]
        USERS[End Users / External Systems]
    end

    %% Connections
    FILES --> EXTRACT
    DATABASES --> EXTRACT
    APIS --> EXTRACT
    STREAMS --> EXTRACT

    EXTRACT --> TRANSFORM
    TRANSFORM --> VALIDATE
    VALIDATE --> LOAD
    TRANSFORM --> METADATA
    LOAD --> VERSIONING
    VERSIONING --> WAREHOUSE
    
    WAREHOUSE --- DB_POSTGIS
    WAREHOUSE --- DB_TIMESERIES
    WAREHOUSE --- OBJECT_STORE

    DB_POSTGIS --> DATA_API
    DB_TIMESERIES --> DATA_API
    OBJECT_STORE --> DATA_API
    CACHE --> DATA_API

    DATA_API --> ANALYSIS_MOD
    DATA_API --> APP_MOD
    DATA_API --> USERS

    METADATA -- "Updates" --> DATA_API

    classDef dataprocess fill:#ffe8cc,stroke:#d68400,stroke-width:2px;
    class ETL_Pipeline,Data_Storage_Access dataprocess;
```

## Directory Structure
```
GEO-INFER-DATA/
├── config/              # Configuration for ETL jobs, database connections, storage endpoints
├── docs/                # Detailed documentation, data model schemas, API specs
├── etl/                 # Scripts and configurations for ETL pipelines (e.g., Airflow DAGs, Spark jobs)
├── examples/            # Example scripts for data access, ETL pipeline usage
├── src/                 # Source code
│   └── geo_infer_data/  # Main Python package
│       ├── api/         # Data access API implementations
│       ├── core/        # Core ETL logic, data processing functions, validation rules
│       ├── models/      # Pydantic models for data schemas, metadata
│       ├── connectors/  # Connectors to various data sources and storage backends
│       └── utils/       # Utility functions, helper scripts
├── storage/             # Schemas, configurations for data storage systems (e.g., PostGIS table definitions)
├── tests/               # Unit and integration tests for ETL, data access, validation
└── validation/          # Detailed data validation rule sets, quality check scripts
```

## Getting Started

### Prerequisites
- Python 3.9+
- Docker (recommended for running databases and other services)
- Relevant database client libraries (e.g., psycopg2 for PostgreSQL)
- Optionally, Apache Spark, Apache Airflow for large-scale ETL.

### Installation
```bash
# Clone the GEO-INFER repository if you haven't already
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER/GEO-INFER-DATA

pip install -e .
# or poetry install if pyproject.toml is configured
```

### Configuration
Database connection details, storage endpoint configurations, API keys for external data sources, and ETL pipeline parameters are managed in `config/` (e.g., `database.ini`, `s3_config.yaml`) and/or environment variables.
```bash
# cp config/example_database.ini config/database.ini
# # Edit database.ini with your local/remote database credentials
```

### Running Tests
```bash
pytest tests/
```

## Supported Data Sources

A wide array of geospatial and related data sources are supported, including but not limited to:

-   **Vector Data:** GeoJSON, Shapefile, GeoPackage, KML, TopoJSON, WKT/WKB.
-   **Raster Data:** GeoTIFF (including Cloud-Optimized GeoTIFF - COG), NetCDF, HDF, Zarr, PNG, JPEG.
-   **Tabular & Time Series Data:** CSV, Parquet, Excel, Feather, with spatial attributes or linked to spatial features.
-   **Databases:** PostgreSQL/PostGIS, MySQL, SQLite, and other SQL/NoSQL databases with geospatial capabilities.
-   **Web Services & APIs:** OGC Standards (WMS, WFS, WCS, WPS, SOS), STAC APIs, RESTful APIs providing geospatial data (e.g., weather APIs, demographics APIs).
-   **IoT Sensor Data Streams:** MQTT, Kafka, or direct sensor integrations for real-time geospatial observations.
-   **Open Data Portals:** CKAN, Socrata, and other open government data platforms.
-   **Crowdsourced Data:** OpenStreetMap (OSM) extracts, data from platforms like Ushahidi or Mapillary.

## Data Storage Options

GEO-INFER-DATA is designed to be flexible with storage backends, leveraging the strengths of different systems:

-   **PostgreSQL with PostGIS:** Primary choice for transactional vector data, complex spatial queries, and relational integrity.
-   **MinIO / S3-compatible Object Storage:** Scalable and cost-effective storage for large raster files, raw data archives, and intermediate ETL products.
-   **TimescaleDB (PostgreSQL extension):** Optimized for high-ingestion rates and complex queries on time-series data, including geospatial time series.
-   **Redis:** In-memory data store for caching frequently accessed data, session management, and as a message broker for real-time updates.
-   **Elasticsearch/OpenSearch:** For indexing and searching large volumes of textual and geospatial metadata, and for certain types of spatial queries.
-   **Specialized Geospatial Databases/Engines:** Potential integration with systems like GeoMesa, GeoWave for very large-scale spatio-temporal analytics on distributed key-value stores (e.g., HBase, Accumulo).

## Integration with Other Modules

GEO-INFER-DATA is central to the framework:

-   **GEO-INFER-OPS (Operations):** OPS may orchestrate ETL pipelines defined in DATA (e.g., using Airflow). DATA provides monitoring information about data quality and pipeline status to OPS.
-   **GEO-INFER-SPACE (Spatial Methods) & GEO-INFER-TIME (Temporal Methods):** These modules consume data prepared and served by DATA. They rely on DATA for efficient access to vector, raster, and time-series data for their analytical operations.
-   **GEO-INFER-AI (Artificial Intelligence) & GEO-INFER-ACT (Active Inference):** Training data for machine learning models and input data for active inference agents are sourced through DATA. DATA ensures this data is clean, well-structured, and versioned.
-   **GEO-INFER-SEC (Security):** DATA implements access control policies defined by SEC, ensuring that sensitive geospatial data is protected. Secure data handling protocols are enforced during ETL and storage.
-   **GEO-INFER-API (Interfaces):** The Data Access API component of DATA can be exposed or aggregated through the main GEO-INFER-API module for external consumption.
-   **GEO-INFER-APP (Applications):** User-facing applications query and visualize data made available through DATA's access layers.

## Performance Considerations

Optimizing data operations is crucial. Key strategies include:
-   Efficient spatial and temporal indexing.
-   Use of optimized file formats (e.g., COG, Parquet).
-   Partitioning large datasets.
-   Parallel processing for ETL jobs.
-   Query optimization and caching.
Refer to `docs/PERFORMANCE_GUIDELINES.md` for detailed guidance.

## Data Governance

The module embodies strong data governance principles:

-   **Data Lineage Tracking:** Recording the origin, transformations, and movement of data throughout its lifecycle.
-   **Comprehensive Metadata Management:** Adhering to standards (ISO 19115, Dublin Core, STAC) for discoverability and understanding.
-   **Quality Assurance Workflows:** Automated checks and manual reviews to ensure data accuracy, completeness, and consistency.
-   **Access Control & Privacy Preservation:** Integration with GEO-INFER-SEC to enforce role-based access and apply anonymization/ pseudonymization techniques where needed.
-   **Data Versioning & Audit Trails:** Keeping track of changes to datasets and schema modifications.

## Contributing

Contributions are highly valued. Areas include:
-   Developing new ETL connectors for various data sources.
-   Improving data validation and quality assessment tools.
-   Optimizing storage and query performance for specific backends.
-   Enhancing metadata management capabilities.
-   Adding support for new geospatial data formats or standards.

Follow the contribution guidelines in the main GEO-INFER documentation (`CONTRIBUTING.md`) and any specific guidelines in `GEO-INFER-DATA/docs/CONTRIBUTING_DATA.md` (to be created).

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 