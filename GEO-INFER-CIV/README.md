# GEO-INFER-CIV

**Civic Engagement & Participatory Geospatial Technologies**

## Overview

GEO-INFER-CIV is dedicated to **empowering communities and fostering civic participation** in geospatial data creation, analysis, and decision-making processes. This module provides a suite of tools and methodologies to facilitate collaborative approaches to understanding and addressing complex ecological, urban, and social challenges. It bridges the gap between technical geospatial capabilities and community knowledge, values, and priorities. By enabling participatory mapping, citizen science, and collaborative planning, GEO-INFER-CIV aims to make geospatial information more accessible, relevant, and actionable for diverse public audiences, leading to more equitable, informed, and sustainable outcomes.

## Core Objectives

-   **Democratize Geospatial Information:** Make geospatial tools and data accessible and usable by non-expert community members.
-   **Integrate Local Knowledge:** Provide platforms for capturing, valuing, and integrating local, traditional, and indigenous knowledge with formal scientific data.
-   **Foster Collaboration:** Enable effective collaboration between community members, planners, researchers, and policymakers.
-   **Enhance Transparency & Trust:** Promote open data practices and transparent decision-making processes related to geospatial issues.
-   **Empower Communities:** Equip communities with the tools and information needed to advocate for their interests and participate meaningfully in planning and governance.
-   **Support Citizen Science:** Facilitate community involvement in scientific research and environmental monitoring through geospatial data collection and analysis.

## Key Features

-   **Participatory Mapping & Data Collection Platforms:** User-friendly web and mobile interfaces that allow community members to contribute geospatial data, map local assets and concerns, and share their perspectives on places.
    -   Customizable forms, offline data collection, multimedia uploads (photos, audio, video).
-   **STEW-MAP (Stewardship Mapping and Assessment Project) Toolkit:** Comprehensive tools for identifying, mapping, and analyzing the networks of civic groups, organizations, and individuals involved in environmental stewardship or community improvement.
    -   Includes survey instruments, network visualization, and spatial analysis of stewardship activities.
-   **Community-Driven Spatial Planning & Scenario Tools:** Platforms that enable communities to collaboratively explore different future scenarios, co-design spatial plans, and deliberate on development proposals using interactive maps and visualization.
-   **Citizen Science Project Management:** Support for designing, launching, and managing citizen science projects, including task assignment, data validation workflows, and feedback mechanisms for participants.
-   **Collaborative Decision Support Systems:** Tools that integrate community-generated data and preferences with technical analyses to support multi-criteria decision-making, conflict resolution, and consensus building on geospatial issues.
-   **Geospatial Storytelling & Communication:** Features for creating compelling narratives that combine maps, community data, and multimedia to communicate local issues and project outcomes effectively (integrates with GEO-INFER-COMMS & GEO-INFER-ART).
-   **Accessibility & Inclusivity Features:** Design considerations to ensure tools are accessible to users with varying technical skills, language preferences, and disabilities.

## Community Engagement & Co-Creation Cycle (Conceptual)

```mermaid
graph TD
    subgraph CIV_Cycle as "GEO-INFER-CIV Engagement Cycle"
        A[1. Define Community Needs & Goals]
        B[2. Co-Design Engagement Strategy & Tools]
        C[3. Launch Participatory Data Collection / Mapping]
        D[4. Community Data Validation & Curation]
        E[5. Collaborative Analysis & Interpretation]
        F[6. Co-Develop Solutions / Action Plans]
        G[7. Implement & Monitor Actions]
        H[8. Evaluate Impact & Iterate]
    end

    subgraph Supporting_GEO_INFER_Modules as "Supporting GEO-INFER Modules"
        DATA[DATA: Store & Manage Data]
        SPACE[SPACE: Spatial Analysis]
        TIME[TIME: Temporal Analysis]
        APP[APP: UI/UX Components]
        COMMS[COMMS: Communication]
        NORMS[NORMS: Policy Context]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> A %% Loop back for iterative improvement

    C -->|Collects Data Into| DATA
    D -->|Uses Tools From| APP
    E -->|Utilizes| SPACE
    E -->|Utilizes| TIME
    F -->|Informed By| NORMS
    B & F & G & H -->|Leverages| COMMS
    
    classDef civProcess fill:#fff5e6,stroke:#ffaa00,stroke-width:2px;
    class A,B,C,D,E,F,G,H civProcess;
```

## Directory Structure
```
GEO-INFER-CIV/
├── config/              # Configuration for engagement platforms, survey tools, map layers
├── docs/                # Documentation, guides for facilitators, case studies
├── examples/            # Example participatory mapping projects, STEW-MAP setups
├── src/                 # Source code
│   └── geo_infer_civ/   # Main Python package
│       ├── api/         # API for interacting with civic engagement platforms
│       ├── core/        # Core logic for participatory mapping, STEW-MAP, decision support
│       ├── models/      # Data models for community data, stewardship networks, survey responses
│       ├── platforms/   # Implementations or integrations of specific engagement tools
│       └── utils/       # Utility functions, survey design helpers, accessibility checkers
└── tests/               # Unit and integration tests for CIV tools
```

## Getting Started

### Prerequisites
- Python 3.9+
- Web framework (e.g., FastAPI, Django, Flask) if serving web platforms.
- Frontend JavaScript libraries (e.g., React, Vue, Leaflet, Mapbox GL JS) for interactive maps.
- Database for storing community data (e.g., PostgreSQL/PostGIS).

### Installation
```bash
# Clone the GEO-INFER repository if you haven't already
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER/GEO-INFER-CIV

pip install -e .
# or poetry install if pyproject.toml is configured
```

### Configuration
Platform settings, map layer configurations, survey definitions, and database connections are managed in `config/` files or environment variables.
```bash
# cp config/example_stewmap_config.yaml config/my_stewmap_project.yaml
# # Edit my_stewmap_project.yaml
```

### Running a Civic Engagement Platform (Example)
(This would depend on the specific platform implemented)
```bash
# Example for a Flask or FastAPI based application
# python -m geo_infer_civ.app  # Assuming app.py is the entry point
```

## Engagement Tools & Methodologies

GEO-INFER-CIV offers a diverse toolkit for fostering community participation:

-   **Interactive Participatory Mapping Interfaces:** Web-based tools allowing users to draw points, lines, and polygons, add attributes, upload photos, and comment on specific locations.
-   **Mobile Citizen Science Data Collection Apps:** Native or web-based mobile applications for field data collection, often with offline capabilities, GPS integration, and simple forms.
-   **Stakeholder Identification & Analysis Tools:** Methods to identify key stakeholders in a geospatial context, map their relationships, and analyze their interests and influence.
-   **Community Asset Mapping:** Facilitating communities to identify and map local resources, skills, and assets that can be leveraged for development or resilience.
-   **Collaborative Scenario Planning Tools:** Interactive platforms where community members can explore different future scenarios (e.g., impacts of climate change, new infrastructure) and express preferences.
-   **Consensus Building & Deliberation Frameworks:** Tools and processes (e.g., Nominal Group Technique, Delphi method adapted for spatial issues) to facilitate constructive dialogue and agreement among diverse stakeholders.
-   **Geosurveys & Spatially-Enabled Questionnaires:** Surveys that include questions with a mapping component (e.g., "Where do you feel unsafe?", "Map your usual travel route").

## STEW-MAP Implementation Details

The module aims for a robust implementation of the Stewardship Mapping and Assessment Project (STEW-MAP) methodology:

-   **Survey Design & Deployment:** Configurable survey instruments to collect information about stewardship groups (their mission, activities, geographic focus, resources, networks).
-   **Stewardship Group Mapping:** Tools for geolocating stewardship groups and the areas they care for or manage.
-   **Social Network Analysis of Stewardship Ties:** Analyzing and visualizing the collaborative relationships, information flow, and resource sharing between different stewardship groups.
-   **Spatial Analysis of Stewardship Coverage:** Assessing the geographic distribution of stewardship activities, identifying areas with high or low stewardship density ("hotspots" and "gaps").
-   **Resource & Capacity Assessment:** Aggregating information about the resources, skills, and capacities within the stewardship network.
-   **Impact Assessment Frameworks:** Methodologies to evaluate the collective impact of stewardship activities on environmental or social outcomes.

## Data Collection Methods Supported

-   **Mobile Applications:** For in-field data gathering (points, tracks, photos, form data).
-   **Web-Based Mapping Interfaces:** For desktop or remote data input and annotation.
-   **Online Survey Tools with Spatial Components:** Integrating map-based questions into broader surveys.
-   **Crowdsourcing & Volunteered Geographic Information (VGI):** Platforms for collecting data from a large, distributed group of volunteers.
-   **Integration with Social Media Spatial Data:** (With privacy considerations) analyzing publicly available geotagged social media posts for sentiment or event detection.
-   **Community-Operated Sensor Networks & IoT Devices:** Facilitating the setup and data integration from low-cost environmental sensors deployed by community members.

## Decision Support Features

Tools to aid collaborative and informed decision-making include:

-   **Multi-Criteria Decision Analysis (MCDA) Support:** Frameworks to help groups weigh different criteria and evaluate alternatives for spatial decisions (e.g., AHP, TOPSIS adapted for spatial context).
-   **Spatial Consensus Building Tools:** Visualizations and analytical tools that highlight areas of agreement and disagreement among stakeholders regarding spatial plans or priorities.
-   **Conflict Resolution Frameworks:** Methodologies and facilitation guides for addressing disagreements that arise during participatory processes.
-   **Equity & Justice Considerations:** Tools to analyze the distributional impacts of proposed plans or policies on different demographic groups or vulnerable communities (integrates with GEO-INFER-NORMS).
-   **Collaborative Goal Setting & Indicator Tracking:** Platforms where communities can define shared goals and track progress using relevant geospatial and non-geospatial indicators.

## Integration with Other Modules

GEO-INFER-CIV is highly interconnected:

-   **GEO-INFER-APP:** Provides the user interface components (maps, forms, dashboards) that CIV leverages to build its participatory platforms.
-   **GEO-INFER-DATA:** All data collected through CIV initiatives (community maps, survey responses, sensor data) is managed, stored, and versioned by DATA.
-   **GEO-INFER-SPACE & GEO-INFER-TIME:** Spatial and temporal analysis capabilities from these modules are used to analyze community-generated data, identify patterns, and model scenarios.
-   **GEO-INFER-NORMS:** Provides context on existing regulations, policies, and social norms that inform community discussions and decision-making. CIV can also help identify informal or desired norms.
-   **GEO-INFER-COMMS:** Essential for outreach, recruitment of participants, disseminating findings from civic engagement projects, and facilitating online discussions.
-   **GEO-INFER-ORG:** Participatory governance models explored in CIV can inform the design of DAOs or other organizational structures in ORG.
-   **GEO-INFER-AI:** AI techniques can be used to analyze large volumes of qualitative community input (e.g., text comments on maps), identify themes, or assist in validating crowdsourced data.

## Contributing

We welcome contributions from social scientists, urban planners, community organizers, software developers, and UX designers. Areas include:
-   Developing new participatory mapping tools or features.
-   Improving the STEW-MAP toolkit.
-   Designing and sharing effective community engagement methodologies.
-   Creating case studies and best practice guides.
-   Enhancing accessibility and inclusivity of the tools.
-   Integrating with other civic tech platforms.

Follow the contribution guidelines in the main GEO-INFER documentation (`CONTRIBUTING.md`) and specific guidelines in `GEO-INFER-CIV/docs/CONTRIBUTING_CIV.md` (to be created).

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 