# GEO-INFER-HEALTH

**Geospatial Applications for Public Health, Epidemiology, and Healthcare Accessibility**

## Overview

The GEO-INFER-HEALTH module provides a specialized suite of tools and methodologies for leveraging geospatial information in public health, epidemiology, and healthcare accessibility analysis. It enables users to analyze the spatial dimensions of health-related data, supporting informed decision-making in public health policy, resource allocation, epidemiological research, and emergency response. By integrating with the broader GEO-INFER framework, this module aims to provide a robust platform for understanding and addressing complex health challenges through a geographic lens.

### Documentation
- Module page: ../GEO-INFER-INTRA/docs/modules/geo-infer-health.md
- Modules index: ../GEO-INFER-INTRA/docs/modules/index.md

## Core Objectives

-   **Enhance Disease Surveillance:** Provide advanced tools for real-time or near real-time tracking, mapping, and analysis of disease occurrences and outbreaks.
-   **Improve Healthcare Accessibility Assessment:** Offer robust methods to model, analyze, and visualize access to healthcare services, considering various geographic, social, and economic factors.
-   **Strengthen Environmental Health Analysis:** Facilitate the integration and analysis of environmental data to identify and mitigate spatial risks to public health.
-   **Support Spatial Epidemiology Research:** Equip researchers with tools for investigating the geographic distribution, determinants, and dynamics of health-related states and events.
-   **Reduce Health Disparities:** Enable the identification and analysis of geographic and demographic health inequalities to inform targeted interventions.
-   **Facilitate Public Health Planning & Response:** Provide decision-support tools for optimizing resource allocation, planning interventions, and responding effectively to public health emergencies.

## Key Features

### 1. Advanced Disease Surveillance & Outbreak Modeling
-   **Description:** Tools for mapping disease clusters, identifying statistically significant hotspots, modeling the spatio-temporal spread of infectious diseases, and predicting potential outbreak trajectories.
-   **Techniques/Examples:** Cluster detection algorithms (e.g., SaTScan, Kulldorff's scan statistic adapted for geospatial data), spatio-temporal regression, agent-based models for disease transmission (integrating with GEO-INFER-AGENT and GEO-INFER-SIM), network analysis of contact tracing data.
-   **Benefits:** Early detection of outbreaks, better understanding of transmission dynamics, targeted public health interventions, and optimized resource deployment during epidemics.

### 2. Comprehensive Healthcare Accessibility Analysis
-   **Description:** Methods to assess and visualize physical, economic, and social access to healthcare facilities and services.
-   **Techniques/Examples:** Network analysis for travel time/distance to facilities (integrating GEO-INFER-SPACE), gravity models for service area delineation, two-step floating catchment area (2SFCA) methods, integration of socio-demographic data (from GEO-INFER-DATA) to assess equity.
-   **Benefits:** Identification of underserved areas and populations, informed planning for new facility locations, optimization of existing healthcare networks, and support for policies aimed at improving equitable access.

### 3. Integrated Environmental Health Risk Assessment
-   **Description:** Tools to combine environmental data (e.g., air quality, water pollution, climate factors, proximity to hazards) with health outcome data to assess and map spatial risks to public health.
-   **Techniques/Examples:** Exposure modeling, environmental risk scoring, spatial overlay analysis with pollution plumes or hazard zones, correlation analysis between environmental factors and health conditions. Integration with GEO-INFER-RISK for broader hazard understanding.
-   **Benefits:** Identification of high-risk zones and vulnerable populations, support for environmental justice initiatives, guidance for public health advisories, and input for urban planning and environmental regulation.

### 4. Robust Spatial Epidemiology Toolkit
-   **Description:** A suite of techniques for investigating the geographic distribution and determinants of health-related states or events in specified populations.
-   **Techniques/Examples:** Geographically Weighted Regression (GWR), spatial statistical tests for disease clustering, case-control studies with spatial components, analysis of disease registries. Integration with GEO-INFER-SPM for advanced statistical mapping.
-   **Benefits:** Deeper insights into disease etiology, identification of local risk factors, evidence base for targeted prevention strategies, and contribution to epidemiological research.

### 5. Health Disparities Mapping & Analysis
-   **Description:** Visualization and analytical tools to identify, quantify, and understand health inequalities across different geographic areas and population groups.
-   **Techniques/Examples:** Thematic mapping of health indicators by geographic units, calculation of disparity indices, comparison of health outcomes across different socio-economic or demographic strata within spatial contexts.
-   **Benefits:** Highlights areas and groups disproportionately affected by poor health, informs policies to promote health equity, and monitors progress in reducing disparities.

### 6. Health Data Standards & Interoperability Support
-   **Description:** Capabilities to work with common health data formats and facilitate interoperability with existing health information systems, focusing on spatially relevant data.
-   **Techniques/Examples:** Adapters for health data standards (e.g., de-identified extracts, aggregate data from systems using HL7 FHIR where location is a key attribute), tools for geocoding health records (with appropriate privacy safeguards from GEO-INFER-SEC), integration with public health databases.
-   **Benefits:** Enables the use of existing health data for geospatial analysis, promotes data sharing (where appropriate and secure), and enhances the utility of the GEO-INFER framework in real-world public health settings.

## Data Flow

### Inputs
- **Health Data Sources**:
  - De-identified disease surveillance data (case reports, laboratory results)
  - Healthcare facility locations and service information
  - Population demographics and census data from GEO-INFER-DATA
  - Environmental data (air quality, water quality, climate) from GEO-INFER-SPACE
  - Social determinants of health indicators

- **Configuration Requirements**:
  - `health_config.yaml`: Analysis parameters, privacy settings
  - `data_sources.yaml`: Connection details for health databases
  - Privacy and security configurations via GEO-INFER-SEC

- **Dependencies**:
  - **Required**: GEO-INFER-DATA (base data), GEO-INFER-SPACE (spatial analysis), GEO-INFER-TIME (temporal trends)
  - **Optional**: GEO-INFER-AI (predictive models), GEO-INFER-RISK (hazard data), GEO-INFER-BIO (biological data)

### Processes
- **Disease Surveillance & Monitoring**:
  - Spatial cluster detection and hotspot analysis
  - Temporal trend analysis and outbreak detection
  - Disease mapping and epidemiological curve analysis
  - Contact tracing network analysis

- **Healthcare Accessibility Analysis**:
  - Travel time and distance calculations to facilities
  - Service area delineation and catchment analysis
  - Equity assessment across demographic groups
  - Resource allocation optimization

- **Environmental Health Assessment**:
  - Exposure modeling and risk mapping
  - Correlation analysis between environmental factors and health outcomes
  - Vulnerable population identification
  - Environmental justice analysis

### Outputs
- **Surveillance Products**:
  - Disease distribution maps and epidemiological reports
  - Outbreak alerts and early warning systems
  - Cluster detection results and statistical significance testing
  - Temporal trend visualizations and forecasts

- **Accessibility Maps & Reports**:
  - Healthcare accessibility scores and rankings
  - Service gap analysis and underserved area identification
  - Equity metrics and disparity assessments
  - Facility planning recommendations

- **Integration Points**:
  - Health maps and dashboards via GEO-INFER-APP
  - Risk assessments feed into GEO-INFER-RISK
  - Public health alerts via GEO-INFER-API
  - Policy recommendations for decision makers

## Module Architecture & Components

```mermaid
graph TD
    subgraph HEALTH_Core as "GEO-INFER-HEALTH Core Engine"
        API[API Layer (FastAPI)]
        SERVICE[Service Layer (Business Logic)]
        DATA_ACCESS[Data Access Layer]
        MODELS_HEALTH[Data Models (Pydantic)]
    end

    subgraph Analysis_Engines as "Specialized Analysis Engines"
        DISEASE_SURV[Disease Surveillance Engine]
        ACCESS_ANALYZER[Accessibility Analyzer]
        ENV_RISK_ASSESS[Environmental Risk Assessor]
        SPAT_EPI_TOOLS[Spatial Epidemiology Toolkit]
        DISPARITY_MAPPER[Health Disparity Mapper]
    end

    subgraph Supporting_Tools_Health as "Supporting Tools & Utilities"
        GEO_UTILS_HEALTH[Geospatial Utilities (Leveraging GEO-INFER-SPACE)]
        STAT_UTILS_HEALTH[Statistical Utilities (Leveraging GEO-INFER-MATH, GEO-INFER-SPM)]
        VIS_ADAPTERS_HEALTH[Visualization Adapters (for GEO-INFER-APP)]
        ETL_HEALTH[Health Data ETL (Leveraging GEO-INFER-DATA)]
    end

    subgraph External_Integrations_Health as "External Systems & GEO-INFER Modules"
        DB_HEALTH[(Health Data Storage / Cache)]
        GIS_DATA[GEO-INFER-DATA (Demographics, Environment)]
        SPACE_MOD[GEO-INFER-SPACE (Spatial Operations)]
        TIME_MOD[GEO-INFER-TIME (Temporal Analysis)]
        AI_MOD[GEO-INFER-AI (Predictive Models)]
        AGENT_MOD[GEO-INFER-AGENT (Simulation Agents)]
        SIM_MOD[GEO-INFER-SIM (Simulation Environment)]
        RISK_MOD[GEO-INFER-RISK (Hazard Data)]
        SEC_MOD[GEO-INFER-SEC (Privacy, Anonymization)]
        APP_MOD[GEO-INFER-APP (Visualization)]
    end

    %% Core Engine Connections
    API --> SERVICE
    SERVICE --> MODELS_HEALTH
    SERVICE --> DATA_ACCESS
    DATA_ACCESS --> DB_HEALTH
    DATA_ACCESS --> GIS_DATA

    %% Service Layer to Analysis Engines
    SERVICE --> DISEASE_SURV
    SERVICE --> ACCESS_ANALYZER
    SERVICE --> ENV_RISK_ASSESS
    SERVICE --> SPAT_EPI_TOOLS
    SERVICE --> DISPARITY_MAPPER

    %% Analysis Engines use Supporting Tools
    DISEASE_SURV --> GEO_UTILS_HEALTH; DISEASE_SURV --> STAT_UTILS_HEALTH
    ACCESS_ANALYZER --> GEO_UTILS_HEALTH
    ENV_RISK_ASSESS --> GEO_UTILS_HEALTH; ENV_RISK_ASSESS --> STAT_UTILS_HEALTH
    SPAT_EPI_TOOLS --> STAT_UTILS_HEALTH
    DISPARITY_MAPPER --> GEO_UTILS_HEALTH; DISPARITY_MAPPER --> VIS_ADAPTERS_HEALTH

    %% Analysis Engines integrate with other GEO-INFER Modules
    DISEASE_SURV --> SPACE_MOD; DISEASE_SURV --> TIME_MOD; DISEASE_SURV --> AI_MOD; DISEASE_SURV --> AGENT_MOD; DISEASE_SURV --> SIM_MOD
    ACCESS_ANALYZER --> SPACE_MOD; ACCESS_ANALYZER --> DATA_MOD
    ENV_RISK_ASSESS --> SPACE_MOD; ENV_RISK_ASSESS --> DATA_MOD; ENV_RISK_ASSESS --> RISK_MOD
    SPAT_EPI_TOOLS --> SPACE_MOD; SPAT_EPI_TOOLS --> TIME_MOD; SPAT_EPI_TOOLS --> DATA_MOD

    %% Supporting Tools connections
    ETL_HEALTH --> DATA_ACCESS
    VIS_ADAPTERS_HEALTH --> APP_MOD

    %% Security
    SERVICE -.-> SEC_MOD

    classDef healthmodule fill:#e6fffa,stroke:#009688,stroke-width:2px;
    class HEALTH_Core,Analysis_Engines healthmodule;
```

-   **Core Engine:** Manages overall module operations, API interactions, and data flow.
-   **Specialized Analysis Engines:** Contain the specific algorithms and logic for each key feature area.
-   **Supporting Tools & Utilities:** Provide foundational geospatial, statistical, visualization, and ETL capabilities, often by leveraging other core GEO-INFER modules.
-   **External Integrations:** Interfaces with other GEO-INFER modules for data, spatial/temporal operations, AI, simulation, and security, as well as dedicated data storage.

## Integration with other GEO-INFER Modules

GEO-INFER-HEALTH functions as an integral part of the wider GEO-INFER ecosystem:

-   **GEO-INFER-DATA:** Essential for accessing, managing, and processing foundational geospatial data (e.g., administrative boundaries, demographics, environmental layers, points of interest) and health-related datasets (e.g., de-identified case data, facility locations). `ETL_HEALTH` components utilize DATA for data ingestion and preparation.
-   **GEO-INFER-SPACE:** Provides the core spatial analysis functions, geometric operations, network analysis, and spatial indexing required for many health analyses (e.g., proximity calculations, catchment area definition, spatial clustering).
-   **GEO-INFER-TIME:** Crucial for analyzing temporal trends in disease incidence, tracking changes in healthcare accessibility over time, or modeling the temporal dynamics of environmental exposures.
-   **GEO-INFER-AI & GEO-INFER-AGENT:** Can be used to develop predictive models for disease outbreaks (AI), or to simulate population behaviors and disease transmission dynamics (AGENT within SIM).
-   **GEO-INFER-SIM:** Provides the environment to run agent-based models or other simulations relevant to health, such as modeling intervention impacts or resource allocation scenarios.
-   **GEO-INFER-RISK:** Can provide data and models on environmental hazards (e.g., flood zones, pollution sources) that are inputs into environmental health risk assessments.
-   **GEO-INFER-SEC:** Critical for ensuring that health data, which is often sensitive, is handled according to privacy regulations, including anonymization of spatial data before analysis or sharing.
-   **GEO-INFER-APP:** Serves as the frontend for visualizing outputs from the HEALTH module, such as interactive maps of disease hotspots, accessibility dashboards, or environmental risk maps.
-   **GEO-INFER-BIO:** May provide insights into pathogen characteristics or population genetics that can inform epidemiological models within HEALTH.
-   **GEO-INFER-SPM:** Offers advanced statistical parametric mapping techniques that can be applied to health data for rigorous spatiotemporal analysis.

## Getting Started

### Prerequisites
-   Python 3.9+
-   Core GEO-INFER framework installed.
-   Relevant geospatial libraries (e.g., GeoPandas, Shapely, Rasterio, NetworkX).
-   Statistical libraries (e.g., SciPy, Statsmodels).
-   Access to health, demographic, and environmental datasets.

### Installation
```bash
pip install -e ./GEO-INFER-HEALTH
```

### Configuration
Module-specific configurations, such as paths to standard datasets, API keys for health data services (if any), or default parameters for analyses, would typically be managed in YAML files within a `config/` directory (e.g., `GEO-INFER-HEALTH/config/health_config.yaml`). Sensitive credentials should be handled via environment variables or a secure configuration provider integrated with GEO-INFER-OPS.

### Basic Usage Example (Illustrative)
```python
from geo_infer_health.api import HealthAPI  # Conceptual API
from geo_infer_health.models import DiseaseReport # Conceptual data model

# Initialize the Health module's API
health_analyzer = HealthAPI(config_path="GEO-INFER-HEALTH/config/health_config.yaml")

# Example: Analyze reported disease cases
# Assuming DiseaseReport is a Pydantic model for case data including location and time
case_data_path = "path/to/deidentified_disease_cases.csv"
disease_reports = [] # Load and parse data into DiseaseReport objects

# Perform hotspot analysis
# hotspots_results = health_analyzer.detect_disease_hotspots(
#    reports=disease_reports,
#    spatial_resolution_m=1000, # e.g., 1km
#    time_window_days=14
# )

# Example: Assess healthcare accessibility
# facility_data_path = "path/to/health_facilities.geojson"
# population_data_path = "path/to/population_grid.geojson"
# accessibility_map = health_analyzer.calculate_accessibility(
#    facilities_path=facility_data_path,
#    population_path=population_data_path,
#    travel_mode="driving",
#    max_travel_time_min=60
# )

# print(f"Hotspot Analysis Results: {hotspots_results}")
# accessibility_map.save("outputs/healthcare_accessibility.geojson")
```

## Data Models (Conceptual Examples)

The `GEO-INFER-HEALTH` module would utilize Pydantic models for structuring its data, for example:

-   `DiseaseCaseRecord`: Represents an individual disease case with attributes like location (anonymized or aggregated), date of onset, demographics.
-   `HealthFacility`: Information about a healthcare facility, including location, type, capacity, services offered.
-   `EnvironmentalExposure`: Data linking locations to levels of specific environmental hazards or pollutants over time.
-   `AccessibilityResult`: Output of accessibility analyses, often a GeoDataFrame with scores for different areas.
-   `RiskAssessmentZone`: A geographic area with associated health risk scores based on various factors.

(Detailed schemas would be defined in `src/geo_infer_health/models/data_models.py`)

## API Reference

(Placeholder: Detailed API documentation, potentially auto-generated using tools like FastAPI's Swagger/OpenAPI generation, would be linked here. This would cover endpoints for triggering analyses, retrieving results, and managing configurations.)

## Directory Structure
```
GEO-INFER-HEALTH/
├── config/                 # Configuration files for the health module
├── docs/                   # Detailed documentation, methodology descriptions
├── examples/               # Example scripts and notebooks showcasing use cases
│   ├── example_disease_surveillance.py
│   ├── example_healthcare_accessibility.py
│   └── example_environmental_health.py
├── src/
│   └── geo_infer_health/
│       ├── __init__.py
│       ├── api/            # API endpoints and interface definitions
│       │   ├── __init__.py
│       │   ├── api_disease_surveillance.py
│       │   ├── api_healthcare_accessibility.py
│       │   └── api_environmental_health.py
│       ├── core/           # Core algorithms and business logic
│       │   ├── __init__.py
│       │   ├── disease_surveillance.py
│       │   ├── healthcare_accessibility.py
│       │   └── environmental_health.py
│       ├── models/         # Pydantic data models for health-related entities
│       │   ├── __init__.py
│       │   └── data_models.py
│       └── utils/          # Utility functions, data parsers, specific geospatial helpers
│           ├── __init__.py
│           └── geospatial_utils.py # Health-specific geospatial utilities
└── tests/                  # Unit and integration tests
    └── __init__.py
```

## Future Development

-   Enhanced integration with real-time health data streams (e.g., syndromic surveillance).
-   Development of more sophisticated predictive models for disease forecasting, incorporating climate and mobility data.
-   Advanced tools for modeling the impact of health interventions and policy changes.
-   Expansion of support for international health data standards and ontologies.
-   Tools for privacy-preserving federated learning on distributed health datasets.
-   Integration of genomic data for phylogeographic analysis of pathogen spread.

## Contributing

Contributions are highly welcome! This includes developing new analytical tools, improving existing functionalities, adding more example use cases, enhancing documentation, or reporting bugs. Please refer to the main `CONTRIBUTING.md` in the GEO-INFER root directory and any specific guidelines in `GEO-INFER-HEALTH/docs/CONTRIBUTING_HEALTH.md` (to be created).

## License

This module, as part of the GEO-INFER framework, is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 