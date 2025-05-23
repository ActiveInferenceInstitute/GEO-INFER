# GEO-INFER-ECON

**Spatial Economic Modeling, Analysis, and Policy Evaluation**

## Overview

GEO-INFER-ECON is the specialized module within the GEO-INFER framework dedicated to **integrating economic principles with geospatial analysis**. It provides a comprehensive suite of tools for modeling economic activities, analyzing market dynamics, optimizing resource allocation, and evaluating policy impacts across diverse geographic regions and scales. By explicitly incorporating the "where" into economic models, this module enables a more nuanced, context-aware understanding of economic phenomena, moving beyond traditional aspatial approaches. It supports a range of economic theories and quantitative methods, from spatial econometrics and equilibrium models to agent-based simulations of economic behavior in a spatial context.

## Core Objectives

-   **Spatialize Economic Analysis:** Embed geographic location, distance, accessibility, and spatial interactions as fundamental components of economic models and analyses.
-   **Model Market Dynamics Spatially:** Simulate how markets function across space, considering transportation costs, regional agglomeration economies, and inter-regional trade.
-   **Optimize Resource Allocation:** Provide tools for optimizing the distribution and use of resources (e.g., infrastructure, services, natural resources) considering both economic efficiency and spatial equity.
-   **Assess Policy Impacts Geographically:** Evaluate the differential impacts of economic policies (e.g., taxes, subsidies, investments, regulations) on various regions and demographic groups.
-   **Understand Regional Economic Development:** Analyze factors driving regional growth, disparities, and structural change, incorporating spatial dependencies and spillover effects.
-   **Integrate Economic and Environmental Modeling:** Facilitate the analysis of trade-offs and synergies between economic activities and environmental outcomes in a spatially explicit manner.

## Key Features

### 1. Spatial Economic Modeling Engine
-   **Description:** A versatile engine for constructing and running various types of spatial economic models.
-   **Model Types/Examples:**
    -   **Spatial Equilibrium Models:** (e.g., regional CGE models, trade models with transport costs like Armington).
    -   **New Economic Geography Models:** Incorporating agglomeration forces, market access, and firm/labor mobility.
    -   **Input-Output Analysis (Spatial):** Analyzing inter-industry linkages and economic impacts with regional disaggregation.
    -   **Land Use-Transport Interaction (LUTI) Models:** Simulating the co-evolution of land use patterns and transportation systems.
-   **Benefits:** Allows for realistic representation of regional economies, analysis of inter-regional dependencies, and forecasting of economic responses to shocks or policy changes.

### 2. Advanced Spatial Econometrics Toolkit
-   **Description:** A suite of econometric methods specifically designed to handle spatial autocorrelation and spatial heterogeneity in economic data.
-   **Techniques/Examples:**
    -   Spatial autoregressive (SAR) models, Spatial error models (SEM), Spatial Durbin models (SDM).
    -   Geographically Weighted Regression (GWR) and its variants.
    -   Spatial panel data models.
    -   Methods for estimating spatial weight matrices (e.g., contiguity, distance-based, k-nearest neighbors).
-   **Benefits:** Provides statistically sound estimates of economic relationships by accounting for spatial effects, leading to more reliable inference and avoiding biased results common in aspatial analyses.

### 3. Agent-Based Economic Simulation (Geospatial)
-   **Description:** Tools for simulating economic systems from the bottom up, modeling the behavior and interactions of individual economic agents (households, firms, consumers) operating within a defined geographic space.
-   **Techniques/Examples:**
    -   Spatially explicit agent-based models of market dynamics, firm location choice, consumer behavior, or innovation diffusion.
    -   Integration with GEO-INFER-AGENT for defining agent behaviors (e.g., utility maximization, bounded rationality) and GEO-INFER-SIM for the simulation environment.
-   **Benefits:** Captures emergent economic phenomena, heterogeneity in agent behavior, and complex interactions that are difficult to model with aggregate approaches. Useful for exploring non-equilibrium dynamics.

### 4. Policy Impact Assessment & Scenario Analysis
-   **Description:** Frameworks for evaluating the likely economic consequences of different policy interventions or external shocks, with a focus on their spatial distribution.
-   **Techniques/Examples:**
    -   Comparing simulation outputs from baseline vs. policy scenarios (e.g., impact of new infrastructure investment, carbon tax, or trade agreement).
    -   Cost-benefit analysis with spatial disaggregation.
    -   Measuring impacts on regional GDP, employment, income distribution, and other key economic indicators.
-   **Benefits:** Supports evidence-based policymaking by providing quantitative estimates of who wins and loses under different policy options, and where these impacts are most pronounced.

### 5. Resource & Infrastructure Optimization (Spatial)
-   **Description:** Optimization algorithms to guide decisions on resource allocation, infrastructure placement, and service delivery, considering economic efficiency and spatial objectives.
-   **Techniques/Examples:**
    -   Location-allocation models for optimal facility placement.
    -   Network optimization for transportation or energy infrastructure.
    -   Spatially explicit resource management models (e.g., for water, forests, fisheries) incorporating economic values.
-   **Benefits:** Helps in making cost-effective investment decisions, improving service delivery, and ensuring sustainable resource use by considering geographical constraints and opportunities.

## Module Architecture (Conceptual)

```mermaid
graph TD
    subgraph ECON_Core as "GEO-INFER-ECON Core Engine"
        API_ECON[API Layer (FastAPI)]
        SERVICE_ECON[Service Layer (Workflow Orchestration)]
        MODEL_EXEC[Model Execution Engine]
        ANALYSIS_TOOLKIT[Analytical Toolkit]
        DATA_ADAPTERS_ECON[Data Adapters (for GEO-INFER-DATA)]
    end

    subgraph Model_Library_ECON as "Economic Model Library"
        SPAT_EQ_MOD[Spatial Equilibrium Models]
        SPAT_IO_MOD[Spatial Input-Output Models]
        CGE_MOD[Computable General Equilibrium (CGE) Models]
        AGENT_ECON_MOD[Agent-Based Economic Models]
        LOCATION_MOD[Location-Allocation Models]
        HEDONIC_MOD[Spatial Hedonic Pricing Models]
    end

    subgraph Analytical_Methods_ECON as "Analytical Methods"
        SPAT_ECONOMETRICS[Spatial Econometrics Engine]
        GWR_ENGINE[GWR Engine]
        NETWORK_ANALYSIS_ECON[Network Analysis (Trade, Transport)]
        POLICY_SIM_FRAMEWORK[Policy Simulation Framework]
    end

    subgraph External_Integrations_ECON as "External Systems & GEO-INFER Modules"
        DB_ECON[(Economic Data Storage / Cache)]
        DATA_MOD_GI[GEO-INFER-DATA (Base Maps, Demographics, Infrastructure)]
        SPACE_MOD_GI[GEO-INFER-SPACE (Spatial Operations, Network Metrics)]
        TIME_MOD_GI[GEO-INFER-TIME (Time-Series Econometrics, Dynamic Models)]
        SIM_MOD_GI[GEO-INFER-SIM (Simulation Environment for ABM)]
        AGENT_MOD_GI[GEO-INFER-AGENT (Behavioral Rules for Economic Agents)]
        AI_MOD_GI[GEO-INFER-AI (Forecasting, Pattern Recognition in Econ Data)]
        MATH_MOD_GI[GEO-INFER-MATH (Optimization, Statistical Functions)]
        APP_MOD_GI[GEO-INFER-APP (Visualization of Economic Maps/Charts)]
    end

    %% Core Engine Connections
    API_ECON --> SERVICE_ECON
    SERVICE_ECON --> MODEL_EXEC
    SERVICE_ECON --> ANALYSIS_TOOLKIT
    SERVICE_ECON --> DATA_ADAPTERS_ECON
    DATA_ADAPTERS_ECON --> DB_ECON
    DATA_ADAPTERS_ECON --> DATA_MOD_GI

    %% Model Execution uses Model Library and Math
    MODEL_EXEC --> SPAT_EQ_MOD; MODEL_EXEC --> SPAT_IO_MOD; MODEL_EXEC --> CGE_MOD; MODEL_EXEC --> AGENT_ECON_MOD; MODEL_EXEC --> LOCATION_MOD; MODEL_EXEC --> HEDONIC_MOD
    MODEL_EXEC --> MATH_MOD_GI
    AGENT_ECON_MOD --> AGENT_MOD_GI
    AGENT_ECON_MOD -.-> SIM_MOD_GI

    %% Analytical Toolkit uses Methods and Math
    ANALYSIS_TOOLKIT --> SPAT_ECONOMETRICS; ANALYSIS_TOOLKIT --> GWR_ENGINE; ANALYSIS_TOOLKIT --> NETWORK_ANALYSIS_ECON; ANALYSIS_TOOLKIT --> POLICY_SIM_FRAMEWORK
    ANALYSIS_TOOLKIT --> MATH_MOD_GI

    %% Integration with other GEO-INFER Modules by various components
    MODEL_EXEC --> SPACE_MOD_GI; MODEL_EXEC --> TIME_MOD_GI
    ANALYSIS_TOOLKIT --> SPACE_MOD_GI; ANALYSIS_TOOLKIT --> TIME_MOD_GI; ANALYSIS_TOOLKIT --> AI_MOD_GI
    SERVICE_ECON --> APP_MOD_GI

    classDef econmodule fill:#fff0e6,stroke:#ff9800,stroke-width:2px;
    class ECON_Core,Model_Library_ECON,Analytical_Methods_ECON econmodule;
```

-   **Core Engine:** Orchestrates workflows, manages model execution, and provides an API.
-   **Economic Model Library:** Contains implementations of various spatial economic model types.
-   **Analytical Methods:** Houses tools for spatial econometrics, policy simulation, and other analytical techniques.
-   **Data Adapters:** Facilitate interaction with economic datasets and base geospatial data from `GEO-INFER-DATA`.

## Integration with other GEO-INFER Modules

GEO-INFER-ECON relies on and complements several other modules:

-   **GEO-INFER-DATA:** Provides access to fundamental geospatial data (administrative boundaries, infrastructure networks, environmental layers) and socio-economic datasets (population, employment, industry statistics) required as inputs for economic models.
-   **GEO-INFER-SPACE:** Critical for all spatial operations, including calculating distances, defining neighborhoods (for spatial weights), performing network analysis (for transport costs), and managing spatial geometries of economic regions or agents.
-   **GEO-INFER-TIME:** Enables dynamic economic modeling, analysis of economic time series, and spatio-temporal econometrics. Essential for modeling growth, cycles, and long-term policy impacts.
-   **GEO-INFER-MATH:** Supplies the core mathematical and statistical functions for econometric estimation, optimization algorithms (for equilibrium models or resource allocation), and numerical methods used in simulations.
-   **GEO-INFER-SIM & GEO-INFER-AGENT:** `SIM` provides the environment and `AGENT` the behavioral rules for running agent-based economic simulations developed within `ECON`.
-   **GEO-INFER-AI:** Can be used for forecasting economic indicators, identifying complex patterns in economic data that inform model building, or creating surrogate models for computationally intensive economic simulations.
-   **GEO-INFER-APP:** Visualizes the outputs of economic analyses, such as maps of regional economic indicators, charts of policy impacts, or interactive dashboards for exploring economic scenarios.
-   **GEO-INFER-RISK:** Economic impacts are a key component of overall risk assessment. ECON can model the economic consequences of natural disasters or other risks analyzed by RISK.
-   **Domain-Specific Modules (e.g., GEO-INFER-AG, GEO-INFER-HEALTH, GEO-INFER-LOG):** ECON can provide the economic modeling framework for these domains (e.g., agricultural economics, health economics, logistics cost-benefit analysis).

## Getting Started

### Prerequisites
-   Python 3.9+
-   Core GEO-INFER framework installed.
-   Standard data science libraries: Pandas, NumPy, SciPy, Statsmodels, Scikit-learn.
-   Geospatial libraries: GeoPandas, Shapely.
-   Access to relevant economic and geospatial datasets.

### Installation
```bash
# Ensure the main GEO-INFER repository is cloned
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER

pip install -e ./GEO-INFER-ECON
# Or if managed by a broader project build system.
```

### Configuration
Configuration for economic models (e.g., parameters, input data paths, regional definitions) and analytical tools are typically managed in YAML files within the `config/` directory (e.g., `GEO-INFER-ECON/config/regional_cge_model.yaml`).

### Basic Usage Example (Illustrative)
```python
import geopandas as gpd
# Assuming conceptual classes from geo_infer_econ
# from geo_infer_econ.models import SpatialComputableGeneralEquilibrium
# from geo_infer_econ.analysis import PolicyImpactAnalyzer
# from geo_infer_econ.utils import load_economic_data, load_spatial_data

# --- 1. Load Data ---
# regions_gdf = load_spatial_data("path/to/regions.geojson")
# base_economic_data = load_economic_data("path/to/regional_io_tables.csv", regions=regions_gdf)

# --- 2. Initialize a Spatial CGE Model ---
# cge_model_config = "GEO-INFER-ECON/config/my_regional_cge_config.yaml"
# spatial_cge = SpatialComputableGeneralEquilibrium(config=cge_model_config,
#                                                 regions=regions_gdf,
#                                                 base_data=base_economic_data)

# --- 3. Calibrate and Solve Baseline Model ---
# baseline_solution = spatial_cge.solve_equilibrium()
# print("Baseline Regional GDPs:", baseline_solution.get_regional_gdp())

# --- 4. Define a Policy Shock and Analyze Impact ---
# policy_analyzer = PolicyImpactAnalyzer(model=spatial_cge, baseline_results=baseline_solution)

# Example: Simulate a 10% increase in transport efficiency in a specific region
# policy_shock = {"parameter": "transport_efficiency", "region_id": "RegionA", "change_percent": 10}
# impact_results = policy_analyzer.analyze_shock(shock_details=policy_shock)

# --- 5. Visualize Results (Conceptual) ---
# impact_results.plot_gdp_change_map(output_path="outputs/gdp_impact_map.png")
# impact_results.generate_summary_report(output_path="outputs/policy_impact_report.pdf")
```

## Economic Modeling Capabilities (Examples)

-   **Spatial Equilibrium Models:** Regional trade, labor mobility, land markets.
-   **Input-Output Analysis:** Quantifying inter-industry dependencies and multipliers at sub-national levels.
-   **Computable General Equilibrium (CGE) Models:** Simulating economy-wide impacts of policies or external shocks, considering inter-sectoral linkages and resource constraints, disaggregated spatially.
-   **Agent-Based Economic Models:** Modeling firm location decisions, consumer choice with spatial preferences, innovation diffusion across regions.
-   **Location-Allocation Models:** Optimizing the placement of public services or commercial facilities considering demand, accessibility, and costs.
-   **Spatial Hedonic Pricing Models:** Estimating the implicit value of location-specific amenities (e.g., proximity to parks, school quality) as reflected in property prices.

## Application Domains

-   **Urban Economics & Land Use Planning:** Modeling urban growth, housing markets, impacts of zoning.
-   **Transportation Economics:** Analyzing impacts of infrastructure investments, congestion pricing, accessibility changes.
-   **Environmental & Resource Economics:** Valuing ecosystem services, modeling pollution impacts, analyzing resource extraction policies.
-   **Regional Science & Development:** Understanding regional disparities, convergence, and impacts of development policies.
-   **Agricultural Economics:** Modeling land allocation, market access for agricultural products, impacts of climate change on farm income (integrates with GEO-INFER-AG).
-   **International Trade:** Analyzing trade flows between regions/countries, impacts of trade policies considering geography.
-   **Public Finance:** Assessing spatial incidence of taxes and benefits of public expenditures.

## Directory Structure
```
GEO-INFER-ECON/
├── config/               # Configuration files for models, scenarios, data sources
├── docs/                 # Detailed documentation, economic theory background
├── examples/             # Example scripts and notebooks for various economic analyses
├── src/
│   └── geo_infer_econ/
│       ├── __init__.py
│       ├── api/          # API endpoints for economic modeling services
│       ├── core/         # Core analytical engines, model solvers, workflow managers
│       ├── models/       # Implementations of specific economic model types (CGE, ABM, I/O etc.)
│       ├── econometrics/ # Spatial econometric tools and functions
│       └── utils/        # Utility functions for data handling, visualization adapters
└── tests/                # Unit and integration tests for models and analyses
```

## Future Development

-   Enhanced integration with dynamic general equilibrium models (DSGE) with spatial components.
-   Development of more sophisticated agent-based models for financial markets or innovation ecosystems in a spatial context.
-   Tools for microsimulation of household economic behavior and distributional impacts of policies.
-   Improved calibration techniques for complex spatial economic models using AI/ML methods.
-   Closer integration with GEO-INFER-NORMS for modeling the economic impacts of regulations and institutional changes.

## Contributing

Contributions are highly encouraged! This can involve developing new spatial economic models, adding advanced econometric techniques, creating example use cases, improving documentation, or enhancing the integration with other GEO-INFER modules. Please refer to the main `CONTRIBUTING.md` in the GEO-INFER root directory and any specific guidelines in `GEO-INFER-ECON/docs/CONTRIBUTING_ECON.md` (to be created).

## License

This module, as part of the GEO-INFER framework, is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 