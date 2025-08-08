# GEO-INFER-PEP

**People, Engagement, and Performance (PEP) Management**

## Overview

The GEO-INFER-PEP module is a comprehensive solution for managing all aspects of people operations within the GEO-INFER framework and its associated ecosystem. It encompasses functionalities for Human Resources (HR), Customer/Community Relationship Management (CRM), talent acquisition and management, skills development, performance tracking, community engagement, and conflict resolution. This module aims to provide robust tools for data import, transformation, analysis, reporting, and visualization related to all people-centric data, fostering a productive, engaged, and well-supported community and workforce.

### Documentation
- Module page: ../GEO-INFER-INTRA/docs/modules/geo-infer-pep.md
- Modules index: ../GEO-INFER-INTRA/docs/modules/index.md

## Core Objectives

- **Streamline People Operations:** Automate and simplify HR, recruitment, and CRM processes.
- **Enhance Engagement:** Foster strong relationships with employees, contributors, users, and stakeholders.
- **Develop Talent:** Identify skill gaps, facilitate learning, and support career growth within the ecosystem.
- **Optimize Performance:** Implement fair and effective performance management systems.
- **Build Community:** Provide tools for managing and nurturing the GEO-INFER community.
- **Data-Driven Insights:** Enable informed decision-making through comprehensive reporting and analytics on people-related data.

## Key Features

-   **Human Resources Management:** Employee/contributor records, payroll/stipend considerations, benefits administration (if applicable), compliance tracking.
-   **Talent Acquisition & Management:** Recruitment pipeline for contributors and roles, candidate tracking, onboarding processes, skills inventory, competency mapping, career/contribution development planning.
-   **Performance Management:** Goal setting (OKRs, KPIs), performance reviews/feedback cycles, peer feedback mechanisms, competency assessment and tracking.
-   **Community & Stakeholder Relationship Management (CRM):** Contact management for users, partners, and stakeholders, interaction tracking, communication history, segmentation for targeted outreach.
-   **Community Engagement & Moderation:** Tools for managing online community platforms, tracking engagement metrics, facilitating discussions, and implementing moderation policies.
-   **Learning & Development (L&D):** Tracking participation in training or workshops, skill gap analysis based on project needs, personalized learning path recommendations, knowledge sharing platform integration.
-   **Reporting & Analytics:** Customizable dashboards, key performance indicators (KPIs) for HR, talent, and community engagement, trend analysis, predictive analytics (e.g., contributor churn, skill shortages).
-   **Conflict Resolution & Grievance Handling:** Case management for disputes or issues, tracking mediation processes, analyzing resolution effectiveness and patterns.
-   **Surveys & Feedback Collection:** Tools for designing, distributing, and analyzing surveys for employee, community, or stakeholder feedback.
-   **API Access:** Secure and well-documented API for integration with other GEO-INFER modules (e.g., GEO-INFER-ORG for DAO membership) and external systems.

## Module Architecture & Components

```mermaid
graph TD
    subgraph PEP_Core as "GEO-INFER-PEP Core Engine"
        API[API Layer]
        SERVICE[Service Layer]
        DATA_ACCESS[Data Access Layer]
        MODELS[Data Models (Pydantic)]
    end

    subgraph Functional_Modules as "Functional Modules"
        HRM[HR Management]
        TALENT[Talent Acquisition & Development]
        PERF[Performance Management]
        CRM[Community/Stakeholder CRM]
        ENGAGE[Community Engagement]
        LnD[Learning & Development]
        CONFLICT[Conflict Resolution]
    end

    subgraph Supporting_Tools as "Supporting Tools"
        REPORTING[Reporting & Analytics]
        VISUAL[Visualization Engine]
        SURVEY[Survey Engine]
        UTILS[Utility Functions]
        ETL[Data Import/Export (ETL)]
    end

    subgraph External_Systems as "External Systems & Data"
        DB[(PEP Database)]
        ORG_MODULE[GEO-INFER-ORG]
        COMMS_MODULE[GEO-INFER-COMMS]
        EXTERNAL_HRIS[External HRIS/ATS]
        COMM_PLATFORMS[Community Platforms]
    end

    %% Core Engine Connections
    API --> SERVICE
    SERVICE --> DATA_ACCESS
    SERVICE --> MODELS
    DATA_ACCESS --> MODELS
    DATA_ACCESS --> DB

    %% Functional Modules to Core
    HRM --> SERVICE
    TALENT --> SERVICE
    PERF --> SERVICE
    CRM --> SERVICE
    ENGAGE --> SERVICE
    LnD --> SERVICE
    CONFLICT --> SERVICE

    %% Supporting Tools to Core & Functional Modules
    REPORTING --> DATA_ACCESS
    VISUAL --> REPORTING
    SURVEY --> DATA_ACCESS
    SURVEY --> SERVICE
    UTILS --> SERVICE
    ETL --> DATA_ACCESS
    ETL --> EXTERNAL_HRIS

    %% Integration with other GEO-INFER Modules
    SERVICE --> ORG_MODULE
    SERVICE --> COMMS_MODULE
    ENGAGE --> COMM_PLATFORMS

    classDef pepmodule fill:#e0f0ff,stroke:#36c,stroke-width:2px;
    class PEP_Core,Functional_Modules pepmodule;
```

-   **Core Engine:**
    -   `API Layer`: Exposes PEP functionalities to other modules and external applications.
    -   `Service Layer`: Contains the core business logic for each functional area.
    -   `Data Access Layer`: Manages interactions with the PEP database.
    -   `Data Models`: Pydantic schemas defining the structure of people-related data.
-   **Functional Modules:**
    -   `HR Management (src/geo_infer_pep/hr/)`: Handles core HR processes.
    -   `Talent Acquisition & Development (src/geo_infer_pep/talent/)`: Manages recruitment, onboarding, skills, and growth.
    -   `Performance Management`: Oversees goal setting, reviews, and feedback.
    -   `Community/Stakeholder CRM (src/geo_infer_pep/crm/)`: Manages relationships with external parties.
    -   `Community Engagement`: Tools for fostering and managing the GEO-INFER community.
    -   `Learning & Development`: Supports training and skill enhancement.
    -   `Conflict Resolution`: Provides mechanisms for addressing disputes.
-   **Supporting Tools:**
    -   `Reporting & Analytics (src/geo_infer_pep/reporting/)`: Generates reports and insights.
    -   `Visualization Engine (src/geo_infer_pep/visualizations/)`: Creates visual representations of PEP data.
    -   `Survey Engine`: For creating and managing feedback surveys.
    -   `Data Import/Export (ETL)`: For integrating with external data sources.
    -   `Utility Functions (src/geo_infer_pep/utils/)`.
-   `methods.py (src/geo_infer_pep/methods.py)`: May serve as a high-level orchestrator or facade for common combined operations. It provides functions that combine functionalities from various submodules (CRM, HR, Talent, etc.) to execute complex workflows like employee onboarding or generating comprehensive quarterly reports. These methods are designed to simplify interactions with the PEP module for higher-level processes.

## Integration with other GEO-INFER Modules

- **GEO-INFER-ORG:** PEP manages the profiles of members within organizational structures (e.g., DAOs) defined by ORG. It tracks roles, permissions, and contributions linked to governance.
- **GEO-INFER-COMMS:** PEP data (e.g., contributor spotlights, community statistics) can be fed to COMMS for external dissemination. COMMS tools can be used by PEP for outreach and engagement campaigns.
- **GEO-INFER-GIT & Project Platforms:** PEP can track contributions and activity from version control systems and project management tools to build a holistic view of engagement and performance.
- **GEO-INFER-AI:** AI can be leveraged within PEP for tasks like predictive hiring, skill gap analysis, personalized learning recommendations, and sentiment analysis of community feedback.

## Getting Started

### Prerequisites

-   Python 3.9+
-   Poetry (for dependency management)
-   Access to relevant databases or data sources (e.g., existing CRM, HRIS, community platforms)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/activeinference/GEO-INFER.git
    cd GEO-INFER/GEO-INFER-PEP
    ```

2.  **Install dependencies:**
    (Ensure `pyproject.toml` is complete and then run `poetry install`)
    ```bash
    poetry install
    ```

### Configuration

Configuration for database connections, API keys for external services (e.g., existing HR/CRM systems, community platforms), and other module-specific settings will be managed via files in the `config/` directory (e.g., `config.yaml`, `.env` files). Detailed instructions will be available in `GEO-INFER-PEP/docs/CONFIGURATION.md`.

## Usage

(Detailed examples and use cases for different functionalities will be added here. This section will cover how to use the various methods and tools provided by the module.)

### Example: Importing CRM Data
```python
# (Illustrative example - actual implementation may vary)
from geo_infer_pep.crm import importer # Assuming an importer submodule
from geo_infer_pep.config import settings # For API keys

# crm_data = importer.import_from_source(source_type="salesforce", 
#                                        api_key=settings.SALESFORCE_API_KEY, 
#                                        last_sync_date="YYYY-MM-DD")
# print(f"Successfully imported {len(crm_data)} CRM records.")
```

### Example: Generating an HR Headcount Report
```python
# (Illustrative example)
from geo_infer_pep.reporting import hr_reports

# headcount_report = hr_reports.generate_headcount_report(department="Core Contributors", as_of_date="YYYY-MM-DD")
# if headcount_report:
#    headcount_report.save_to_format("headcount_report.pdf", format_type="pdf")
```

## API Reference

(Detailed API documentation, potentially auto-generated using FastAPI/Swagger, will be linked here. This will cover all available endpoints, request/response formats, and authentication methods for inter-module communication or external access.)

## Data Models

The module utilizes Pydantic models for data validation and schema definition. Key data models (found in `src/geo_infer_pep/models/`) will include, but are not limited to:
-   `Person` (generalized for employee, contributor, community member)
-   `Role` / `Position`
-   `Skill`
-   `Contribution`
-   `PerformanceCycle`
-   `Feedback`
-   `Community`
-   `InteractionLog` (for CRM and community engagement)
-   `LearningModule`
-   `ConflictCase`

Detailed schemas will be available in the source code and potentially in a dedicated documentation section.

## Development

### Running Tests

The test suite uses `pytest`. Ensure you have installed the development dependencies.
Comprehensive tests for models, importers, transformers, reporting functions, visualizations, and high-level methods are located in the `tests/` directory.

To run all tests:
```bash
poetry run pytest tests/
```

To run tests for a specific file (e.g., CRM tests):
```bash
poetry run pytest tests/test_crm.py
```

To run a specific test function:
```bash
poetry run pytest tests/test_crm.py::test_customer_model
```

### Linting and Formatting

We use `ruff` for linting and formatting to maintain code quality.
```bash
poetry run ruff check .
poetry run ruff format .
```

## Contributing

Please refer to the main `CONTRIBUTING.md` file in the root of the GEO-INFER repository. Specific contribution guidelines for GEO-INFER-PEP, including setting up a development environment and coding standards, will be detailed in `GEO-INFER-PEP/docs/CONTRIBUTING_PEP.md` (to be created).

We welcome contributions in areas such as:
-   Developing new features for HR, Talent, CRM, or Community Engagement.
-   Improving reporting and analytics capabilities.
-   Integrating with new external HR/CRM or community platforms.
-   Enhancing data models and API endpoints.
-   Writing tests and documentation.

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 