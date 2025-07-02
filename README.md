# GEO-INFER Framework 🌍🔍

[![License: CC BY-ND-SA 4.0](https://img.shields.io/badge/License-CC%20BY--ND--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nd-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289DA.svg)](https://discord.activeinference.institute/)


<div align="center">
  <a href="#getting-started-">🚀 Get Started</a> •
  <a href="#module-categories-">📦 Module Categories</a> •
  <a href="#core-modules-">🔧 Core Modules</a> •
  <a href="#use-cases-">📋 Use Cases</a> •
  <a href="#contributing-">👥 Contributing</a> •
  <a href="#community-">🌐 Community</a> •
  <a href="#license-">📄 License</a>
</div>

## Overview 📋

GEO-INFER is a geospatial inference framework designed for ecological, civic, and commercial applications. It provides a modular architecture for spatial-temporal analysis, active inference modeling, and community engagement.

## 📦 Module Categories

```mermaid
mindmap
  root((GEO-INFER))
    Analytical Core
      ACT - Active Inference
      BAYES - Bayesian methods
      AI - Artificial Intelligence
      MATH - Mathematical foundations
      COG - Cognitive modeling
      AGENT - Intelligent Agents
      SPM - Statistical Parametric Mapping
    Spatial-Temporal
      SPACE - Spatial methods
      TIME - Temporal methods
    Data Management
      DATA - Data processing
      API - Interfaces
    Security and Governance
      SEC - Security
      NORMS - Compliance
      REQ - Requirements
    Simulation & Modeling
      SIM - Simulation
      ANT - Complex systems
    People and Community
      CIV - Civic engagement
      PEP - People management
      ORG - Organizations
      COMMS - Communications
    Applications
      APP - User interfaces
      ART - Artistic expression
    Domain-Specific
      AG - Agriculture
      ECON - Economics
      RISK - Risk management
      LOG - Logistics
      BIO - Bioinformatics
      HEALTH - Health Applications
    Operations
      OPS - Orchestration
      INTRA - Documentation
      GIT - Version control
      TEST - Quality Assurance
      EXAMPLES - Cross-module demos
```
## 🧭 Quick Navigation

| Category                     | Modules                                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **🧠 Analytical Core**       | [ACT](./GEO-INFER-ACT/), [BAYES](./GEO-INFER-BAYES/), [AI](./GEO-INFER-AI/), [MATH](./GEO-INFER-MATH/), [COG](./GEO-INFER-COG/), [AGENT](./GEO-INFER-AGENT/), [SPM](./GEO-INFER-SPM/) |
| **🗺️ Spatial-Temporal**     | [SPACE](./GEO-INFER-SPACE/), [TIME](./GEO-INFER-TIME/), [IOT](./GEO-INFER-IOT/)                                                                                                       |
| **💾 Data Management**       | [DATA](./GEO-INFER-DATA/), [API](./GEO-INFER-API/)                                                                                                           |
| **🔒 Security & Governance** | [SEC](./GEO-INFER-SEC/), [NORMS](./GEO-INFER-NORMS/), [REQ](./GEO-INFER-REQ/)                                                                                |
| **🧪 Simulation & Modeling** | [SIM](./GEO-INFER-SIM/), [ANT](./GEO-INFER-ANT/)                                                                                                             |
| **👥 People & Community**    | [CIV](./GEO-INFER-CIV/), [PEP](./GEO-INFER-PEP/), [ORG](./GEO-INFER-ORG/), [COMMS](./GEO-INFER-COMMS/)                                                       |
| **🖥️ Applications**         | [APP](./GEO-INFER-APP/), [ART](./GEO-INFER-ART/)                                                                                                             |
| **🏢 Domain-Specific**       | [AG](./GEO-INFER-AG/), [ECON](./GEO-INFER-ECON/), [RISK](./GEO-INFER-RISK/), [LOG](./GEO-INFER-LOG/), [BIO](./GEO-INFER-BIO/), [HEALTH](./GEO-INFER-HEALTH/)                               |
| **⚙️ Operations**            | [OPS](./GEO-INFER-OPS/), [INTRA](./GEO-INFER-INTRA/), [GIT](./GEO-INFER-GIT/), [TEST](./GEO-INFER-TEST/), [EXAMPLES](./GEO-INFER-EXAMPLES/)                                                    |



## 📊 Module Dependencies Matrix

| Module | Core Dependencies | Optional Dependencies | Provides Services To | Data Flow Direction |
|--------|------------------|--------------------|-------------------|-------------------|
| **OPS** | - | SEC | ALL modules | → All |
| **DATA** | OPS, SEC | - | ALL modules | → All |
| **SPACE** | DATA, MATH | TIME, AI, IOT | AG, HEALTH, SIM, APP, ART | → Domain/App |
| **TIME** | DATA, MATH | SPACE, AI, IOT | AG, HEALTH, ECON, SIM | → Domain/Analytics |
| **IOT** | SPACE, DATA | BAYES, TIME, AI | All sensor-based modules | → Sensor/Real-time |
| **AI** | DATA, SPACE | TIME, AGENT | All analytical modules | → Analytics/Prediction |
| **ACT** | MATH, BAYES | AI, AGENT, SIM | AGENT, SIM, decision systems | → Inference/Decision |
| **BAYES** | MATH | SPACE, TIME | ACT, AI, statistical modules | → Statistical/Inference |
| **MATH** | - | - | ALL analytical modules | → All analytics |
| **API** | All modules | - | External systems, APP | ↔ External |
| **APP** | API, SPACE | All modules | End users | ← All modules |
| **AGENT** | ACT, AI | SPACE, TIME, SIM | SIM, autonomous systems | ↔ Agent systems |
| **SIM** | SPACE, TIME | AI, AGENT, ACT | Domain modules, decision support | ↔ Simulation systems |
| **AG** | SPACE, TIME, DATA | AI, ECON, SIM | APP, ECON, food systems | ↔ Agricultural systems |
| **HEALTH** | SPACE, TIME, DATA | AI, RISK, BIO, SPM | APP, policy makers | ↔ Health systems |
| **ECON** | SPACE, TIME, DATA | AI, AG, SIM | Policy makers, RISK | ↔ Economic systems |
| **ANT** | ACT, SIM | AI, AGENT | SIM, complex systems | ↔ Complex systems |
| **ART** | SPACE, APP | AI, TIME | APP, visualization | ← Artistic/Creative |
| **BIO** | SPACE, TIME, DATA | AI, HEALTH | HEALTH, research | ↔ Biological systems |
| **COG** | SPACE, AI | ACT, AGENT | AGENT, human factors | → Cognitive modeling |
| **COMMS** | INTRA, APP | ALL modules | External stakeholders | ← All modules |
| **GIT** | OPS | - | All development | → Version control |
| **INTRA** | - | ALL modules | Documentation, standards | ← All modules |
| **LOG** | SPACE, TIME, DATA | AI, SIM | ECON, operations | ↔ Logistics systems |
| **NORMS** | SPACE, DATA | REQ, SEC | All compliance | → Regulatory/Ethics |
| **ORG** | PEP, COMMS | CIV, NORMS | Governance systems | ↔ Organizational |
| **PEP** | ORG, COMMS | CIV | HR, community | ↔ People management |
| **REQ** | NORMS, SEC | ALL modules | System specifications | → Requirements |
| **RISK** | SPACE, TIME, DATA | AI, HEALTH, ECON | Decision support | ↔ Risk assessment |
| **SEC** | - | ALL modules | Security services | → All modules |
| **SPM** | MATH, SPACE | TIME, BAYES | Statistical analysis | → Statistical mapping |
| **TEST** | ALL modules | - | Quality assurance | ← All modules |
| **EXAMPLES** | All modules | - | New users, developers | ← All modules (demo only) |

### Legend
- **→** : Provides data/services to  
- **←** : Consumes data/services from  
- **↔** : Bidirectional data exchange

## Core Modules (Enhanced)

| **Module Name**     | **Purpose**                                                                                        | **Input Types** | **Output Types** | **Dependencies** | **Status** |
| ------------------- | -------------------------------------------------------------------------------------------------- | --------------- | ---------------- | ---------------- | ---------- |
| **GEO-INFER-ACT**   | [Active Inference modeling for nested and interacting systems](./GEO-INFER-ACT/README.md) | Observations, beliefs, policies, generative models | Belief updates, action selections, free energy estimates | MATH, BAYES | Stable |
| **GEO-INFER-AG**    | [Agricultural methods and farming applications](./GEO-INFER-AG/README.md) | Satellite imagery, soil data, weather data, field boundaries | Yield predictions, crop health maps, precision agriculture recommendations | SPACE, TIME, DATA | Beta |
| **GEO-INFER-AI**    | [Artificial Intelligence and Machine Learning for geospatial workflows](./GEO-INFER-AI/README.md) | Imagery, spatial features, training labels, time-series data | Trained models, predictions, classifications, forecasts | DATA, SPACE | Beta |
| **GEO-INFER-AGENT** | [Intelligent agent frameworks for autonomous geospatial decision-making](./GEO-INFER-AGENT/README.md) | Agent configurations, spatial environments, behavior rules | Autonomous decisions, agent interactions, simulation results | ACT, AI | Beta |
| **GEO-INFER-ANT**   | [Complex systems modeling using Active Inference principles](./GEO-INFER-ANT/README.md) | Movement data, colony parameters, environmental conditions | Emergent behaviors, optimization solutions, swarm dynamics | ACT, SIM | Alpha |
| **GEO-INFER-API**   | [API development and integration services for interoperability](./GEO-INFER-API/README.md) | Module functions, data requests, external API calls | REST/GraphQL APIs, webhooks, standardized responses | All modules | Beta |
| **GEO-INFER-APP**   | [User interfaces, accessibility tools, and application development](./GEO-INFER-APP/README.md) | Analysis results, data products, user interactions | Interactive maps, dashboards, reports, mobile apps | API, SPACE | Beta |
| **GEO-INFER-ART**   | [Art production and aesthetics with geospatial dimensions](./GEO-INFER-ART/README.md) | Geospatial data, artistic parameters, aesthetic rules | Artistic visualizations, generative maps, aesthetic frameworks | SPACE, APP | Alpha |
| **GEO-INFER-BAYES** | [Generalized Bayesian inference processes](./GEO-INFER-BAYES/README.md) | Observations, priors, model specifications | Posterior distributions, uncertainty estimates, model evidence | MATH | Stable |
| **GEO-INFER-BIO**   | [Bioinformatics analysis with spatial context](./GEO-INFER-BIO/README.md) | Genomic data, biological sequences, sample locations | Spatial omics analysis, phylogeographic patterns, ecological modeling | SPACE, TIME, DATA | Beta |
| **GEO-INFER-CIV**   | [Community engagement and participatory mapping tools](./GEO-INFER-CIV/README.md) | Community input, stakeholder data, participatory mapping | STEW-MAP visualizations, community-driven spatial planning | SPACE, APP | Alpha |
| **GEO-INFER-COG**   | [Cognitive phenomena and modeling for geospatial systems](./GEO-INFER-COG/README.md) | User behavior, cognitive models, spatial perception data | Attention mechanisms, spatial memory models, trust modeling | SPACE, AI | Alpha |
| **GEO-INFER-COMMS** | [Communications within and outside of the project](./GEO-INFER-COMMS/README.md) | Project communications, documentation needs, outreach requirements | Communication strategies, documentation, public engagement | INTRA, APP | Alpha |
| **GEO-INFER-DATA**  | [Data management, ETL processes, and storage optimization](./GEO-INFER-DATA/README.md) | Raw geospatial data, external APIs, sensor feeds | Processed datasets, data pipelines, storage solutions | OPS, SEC | Beta |
| **GEO-INFER-ECON**  | [Economic modeling with spatial dimensions](./GEO-INFER-ECON/README.md) | Economic indicators, market data, spatial boundaries | Economic models, policy analysis, market simulations | SPACE, TIME, DATA | Beta |
| **GEO-INFER-GIT**   | [Git integration and version control workflows](./GEO-INFER-GIT/README.md) | Repository configurations, version control needs | Automated versioning, repository management, CI/CD integration | OPS | Beta |
| **GEO-INFER-HEALTH** | [Geospatial applications for public health and epidemiology](./GEO-INFER-HEALTH/README.md) | Health data, epidemiological records, environmental factors | Disease surveillance, healthcare accessibility analysis, health risk assessment | SPACE, TIME, DATA | Beta |
| **GEO-INFER-INTRA** | [Project documentation, workflows, and ontology management](./GEO-INFER-INTRA/README.md) | Project requirements, documentation needs, ontological structures | Comprehensive documentation, workflow templates, standardized ontologies | All modules | Beta |
| **GEO-INFER-IOT** | [Internet of Things sensors and spatial web integration](./GEO-INFER-IOT/README.md) | IoT sensor streams, device metadata, spatial coordinates | Real-time sensor data fusion, Bayesian spatial interpolation, global sensor networks | SPACE, BAYES, DATA | Beta |
| **GEO-INFER-MATH**  | [Mathematical foundations and computational methods](./GEO-INFER-MATH/README.md) | Mathematical problems, spatial calculations, statistical requirements | Mathematical solutions, spatial statistics, optimization results | - | Stable |
| **GEO-INFER-NORMS** | [Social-technical compliance modeling](./GEO-INFER-NORMS/README.md) | Regulatory requirements, compliance data, social norms | Compliance tracking, regulatory impact mapping, social norm modeling | SPACE, DATA | Alpha |
| **GEO-INFER-OPS**   | [Operational kernel for system orchestration and monitoring](./GEO-INFER-OPS/README.md) | System metrics, configuration files, infrastructure requirements | Monitoring dashboards, automated deployment, system health reports | SEC | Stable |
| **GEO-INFER-ORG**   | [Organizations and Decentralized Autonomous Organizations](./GEO-INFER-ORG/README.md) | Organizational structures, governance requirements, DAO parameters | Governance frameworks, token engineering, proposal systems | PEP, COMMS | Alpha |
| **GEO-INFER-PEP**   | [People management, HR, and CRM functions](./GEO-INFER-PEP/README.md) | Personnel data, community relationships, skill requirements | Talent management, community engagement, conflict resolution | ORG, COMMS | Alpha |
| **GEO-INFER-REQ**   | [Requirements engineering using P3IF framework](./GEO-INFER-REQ/README.md) | Requirements specifications, stakeholder needs, system constraints | Validated requirements, compliance frameworks, system specifications | NORMS, SEC | Alpha |
| **GEO-INFER-SEC**   | [Security and privacy frameworks for geospatial information](./GEO-INFER-SEC/README.md) | Security requirements, privacy constraints, access control needs | Security protocols, data anonymization, compliance frameworks | - | Beta |
| **GEO-INFER-SIM**   | [Simulation environments for hypothesis testing](./GEO-INFER-SIM/README.md) | Model parameters, scenario definitions, simulation requirements | Digital twins, agent-based models, scenario planning tools | SPACE, TIME | Alpha |
| **GEO-INFER-SPM**   | [Statistical Parametric Mapping for spatial-temporal analysis](./GEO-INFER-SPM/README.md) | Spatial-temporal data, statistical models, field observations | GLM analysis, random field theory, cluster-level inference | MATH, SPACE | Alpha |
| **GEO-INFER-SPACE** | [Advanced spatial methods for comprehensive geospatial analysis](./GEO-INFER-SPACE/README.md) | Vector/raster data, coordinates, geometries, spatial queries | Processed spatial data, analysis results, spatial indices | DATA, MATH | Stable |
| **GEO-INFER-TIME**  | [Temporal methods for timeline expression and dynamic data fusion](./GEO-INFER-TIME/README.md) | Time-series data, sensor streams, historical records | Forecasts, trends, temporal patterns, events | DATA, MATH | Stable |
| **GEO-INFER-RISK**  | [Risk modeling and insurance for geospatial applications](./GEO-INFER-RISK/README.md) | Risk factors, hazard data, vulnerability assessments | Risk models, insurance pricing, exposure management | SPACE, TIME, DATA | Alpha |
| **GEO-INFER-LOG**   | [Logistics and supply chain optimization](./GEO-INFER-LOG/README.md) | Transportation networks, supply chain data, logistics requirements | Route optimization, supply chain modeling, logistics planning | SPACE, TIME, DATA | Alpha |
| **GEO-INFER-TEST**  | [Comprehensive testing framework for quality assurance](./GEO-INFER-TEST/README.md) | Test requirements, quality metrics, integration needs | Automated test suites, quality reports, integration validation | All modules | Beta |
| **GEO-INFER-EXAMPLES** | [Cross-module integration demonstrations and tutorials](./GEO-INFER-EXAMPLES/README.md) | Integration requirements, tutorial needs, demonstration scenarios | Integration examples, best practices, entry-point tutorials | All modules | Beta |

## 🔄 Framework Position in Geospatial Ecosystem

```mermaid
graph TD
    classDef mainNode fill:#ff9e80,stroke:#d50000,stroke-width:2px
    classDef sourceNode fill:#80d8ff,stroke:#0091ea,stroke-width:1px
    classDef applicationNode fill:#b9f6ca,stroke:#00c853,stroke-width:1px
    classDef domainNode fill:#e1bee7,stroke:#8e24aa,stroke-width:1px

    GEOINFER[GEO-INFER Framework]:::mainNode
    
    %% Data Sources
    RS[Remote Sensing]:::sourceNode
    IOT[IoT Sensors]:::sourceNode
    CSV[Tabular Data]:::sourceNode
    OSM[OpenStreetMap]:::sourceNode
    CGD[Crowdsourced Geodata]:::sourceNode
    
    %% Applications
    DT[Digital Twins]:::applicationNode
    CSD[Climate-Smart Decisions]:::applicationNode
    ES[Ecological Simulations]:::applicationNode
    CP[Civic Planning]:::applicationNode
    RM[Risk Management]:::applicationNode
    
    %% Domains
    URB[Urban Systems]:::domainNode
    ECO[Ecosystems]:::domainNode
    AGR[Agriculture]:::domainNode
    CLI[Climate]:::domainNode
    DIS[Disaster Response]:::domainNode
    
    %% Connections - Sources to GEO-INFER
    RS --> GEOINFER
    IOT --> GEOINFER
    CSV --> GEOINFER
    OSM --> GEOINFER
    CGD --> GEOINFER
    
    %% Connections - GEO-INFER to Applications
    GEOINFER --> DT
    GEOINFER --> CSD
    GEOINFER --> ES
    GEOINFER --> CP
    GEOINFER --> RM
    
    %% Connections - Applications to Domains
    DT --> URB
    DT --> ECO
    CSD --> CLI
    CSD --> AGR
    ES --> ECO
    ES --> CLI
    CP --> URB
    CP --> DIS
    RM --> DIS
    RM --> AGR
```



## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- Docker (optional)
### Installation
```bash
# Clone the repository
git clone https://github.com/activeinference/GEO-INFER.git
cd GEO-INFER

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
### Quick Start

**Recommended: Start with Examples**
```bash
# Explore comprehensive examples demonstrating module integration
cd GEO-INFER-EXAMPLES
python examples/getting_started/basic_integration_demo.py

# See cross-module workflows in action
python examples/health_agriculture_integration/disease_spread_monitoring.py
```

**Direct Module Usage**
```python
from geo_infer import Space, Time, Act

# Initialize core components
space = Space()
time = Time()
act = Act()

# Perform basic spatial-temporal analysis
result = act.analyze(space, time)
```

> 💡 **Pro Tip**: The GEO-INFER-EXAMPLES module provides the best entry point for understanding how modules work together. Each example demonstrates real-world applications using multiple modules in concert.
## 🔄 Framework Integration Guide

### Starting Your GEO-INFER Journey

**For New Users (Start Here):**
1. **Explore Examples First**: Begin with `GEO-INFER-EXAMPLES` to see the framework in action
2. **Install Core Infrastructure**: Set up `GEO-INFER-OPS` for monitoring and `GEO-INFER-DATA` for data management
3. **Add Foundational Modules**: Install `GEO-INFER-SPACE` and `GEO-INFER-MATH` for basic spatial capabilities
4. **Choose Domain Module**: Select one domain module (AG, HEALTH, ECON) based on your use case
5. **Add Analytics**: Include `GEO-INFER-TIME` and/or `GEO-INFER-AI` for advanced analysis
6. **Create Interface**: Use `GEO-INFER-API` and `GEO-INFER-APP` for user access and web presence

### Common Integration Patterns

#### Pattern 1: Health Surveillance System
```
OPS → DATA → SPACE → TIME → HEALTH → API → APP
       ↓       ↓       ↓       ↓        ↓
      SEC → MATH → AI → RISK → SPM
```

#### Pattern 2: Agricultural Monitoring
```
OPS → DATA → SPACE → TIME → AG → AI → SIM → APP
       ↓       ↓       ↓      ↓    ↓    ↓
      SEC → MATH → BAYES → ECON → API
```

#### Pattern 3: Smart City Analytics
```
OPS → DATA → SPACE → TIME → AI → AGENT → SIM → APP
       ↓       ↓       ↓       ↓      ↓       ↓
      SEC → MATH → CIV → RISK → NORMS → API
```

#### Pattern 4: Geospatial Web Application
```
OPS → DATA → SPACE → API → APP → Web Users
       ↓       ↓       ↓       ↓
      SEC → INTRA → COMMS → ART
```

### 📋 Module Integration Quick Reference

| **If You Need...** | **Core Modules** | **Enhancement Modules** | **Example Pattern** |
|---------------------|------------------|-------------------------|-------------------|
| **Basic Spatial Analysis** | DATA + SPACE + MATH | TIME, AI | `DATA → SPACE → MATH → Results` |
| **Active Inference Modeling** | ACT + BAYES + MATH | AGENT, SIM, AI | `BAYES → ACT → AGENT → SIM` |
| **Agricultural Monitoring** | AG + SPACE + TIME | AI, ECON, SIM | `DATA → SPACE → TIME → AG → AI` |
| **Health Surveillance** | HEALTH + SPACE + TIME | AI, RISK, BIO, SPM | `DATA → SPACE → HEALTH → RISK` |
| **Economic Modeling** | ECON + SPACE + TIME | AG, SIM, AI | `DATA → SPACE → ECON → SIM` |
| **Risk Assessment** | RISK + SPACE + TIME | AI, HEALTH, ECON | `DATA → SPACE → RISK → Health` |
| **Complex Systems** | SIM + ANT + ACT | AI, AGENT, SPACE | `ACT → AGENT → ANT → SIM` |
| **Community Engagement** | CIV + APP + COMMS | SPACE, ORG, PEP | `SPACE → CIV → APP → COMMS` |
| **Web Applications** | API + APP + DATA | SPACE, ART, COMMS | `DATA → API → APP → Users` |
| **IoT Sensor Networks** | IOT + BAYES + SPACE | TIME, AI | `IOT → BAYES → SPACE → Analysis` |
| **Research Pipeline** | Multiple modules | EXAMPLES, INTRA, TEST | `Examples → Core → Analysis` |

### Module Compatibility Matrix

| Module | Compatible With | Requires | Enhances |
|--------|----------------|----------|----------|
| **OPS** | All modules | - | System reliability, monitoring |
| **DATA** | All modules | OPS | Data availability, storage |
| **SPACE** | All modules | DATA, MATH | Spatial capabilities, indexing |
| **TIME** | All analytical | DATA, MATH | Temporal analysis, forecasting |
| **IOT** | SPACE, BAYES, sensor modules | AI, TIME | Real-time sensor integration, spatial web |
| **AI** | All analytical | DATA, SPACE | Predictive capabilities, ML |
| **ACT** | BAYES, AGENT, SIM | MATH | Active inference, decision making |
| **BAYES** | ACT, AI, SPM | MATH | Uncertainty quantification |
| **AGENT** | ACT, AI, SIM | - | Autonomous decision making |
| **HEALTH** | SPACE, TIME, AI, BIO, SPM | DATA | Health analytics, surveillance |
| **AG** | SPACE, TIME, AI, ECON | DATA | Agricultural insights, precision farming |
| **BIO** | SPACE, TIME, HEALTH | DATA | Bioinformatics, spatial omics |
| **ECON** | SPACE, TIME, AG, RISK | DATA | Economic modeling, policy analysis |
| **RISK** | SPACE, TIME, HEALTH, ECON | DATA | Risk assessment, insurance |
| **API** | All modules | OPS | External integration, services |
| **APP** | API, SPACE, all domain modules | DATA | User interfaces, visualization |
| **ART** | SPACE, APP | - | Artistic visualization, creativity |
| **SIM** | SPACE, TIME, ACT, AGENT | DATA | Modeling, scenario planning |
| **SPM** | SPACE, MATH, BAYES | - | Statistical parametric mapping |

### Quick Start by Use Case

#### 🏥 Public Health Surveillance
```bash
# Minimal setup for health surveillance
pip install -e ./GEO-INFER-OPS ./GEO-INFER-DATA ./GEO-INFER-SPACE ./GEO-INFER-HEALTH

# Configure health data sources
cp GEO-INFER-HEALTH/config/example.yaml config/health-surveillance.yaml
# Edit to add your health data connections

# Run disease surveillance
python examples/health_surveillance_basic.py
```

#### 🌾 Agricultural Monitoring
```bash
# Setup for crop monitoring
pip install -e ./GEO-INFER-SPACE ./GEO-INFER-TIME ./GEO-INFER-AG ./GEO-INFER-AI

# Run crop analysis
python examples/crop_monitoring_pipeline.py
```

#### 🏙️ Urban Planning
```bash
# Setup for urban analysis
pip install -e ./GEO-INFER-SPACE ./GEO-INFER-CIV ./GEO-INFER-SIM ./GEO-INFER-APP

# Launch urban planning tools
python examples/urban_planning_dashboard.py
```

#### 🌐 Geospatial Web Application Development
```bash
# Setup for web application development
pip install -e ./GEO-INFER-APP ./GEO-INFER-API ./GEO-INFER-COMMS ./GEO-INFER-INTRA

# Generate web application
python examples/generate_geospatial_webapp.py
```

## 📋 Use Cases

### Ecological Applications
- Biodiversity monitoring
- Climate change impact assessment
- Ecosystem service valuation
- Habitat connectivity analysis

### Civic Applications
- Community-based mapping
- Participatory planning
- Environmental justice assessment
- Urban resilience planning

### Research Applications
- Spatial-temporal modeling
- Complex system analysis
- Multi-scale ecological studies
- Interdisciplinary research

## Project Structure 📂

Each module generally follows this standardized structure, though some may include additional directories specific to their domain or function (e.g., `etl/`, `storage/`, `repos/`).
```
MODULE_NAME/
├── config/               # Configuration files
├── docs/                 # Documentation
├── examples/             # Example applications and use cases
├── src/                  # Source code
│   └── module_package/   # Main package
│       ├── api/          # API definitions
│       ├── core/         # Core functionality
│       ├── models/       # Data models
│       └── utils/        # Utility functions
└── tests/                # Test suite
```


The following diagram illustrates the relationships and interactions between all modules in the GEO-INFER framework:

```mermaid
graph TB
    classDef core fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    classDef data fill:#bbdefb,stroke:#1976d2,stroke-width:1px
    classDef analysis fill:#c8e6c9,stroke:#388e3c,stroke-width:1px
    classDef presentation fill:#ffccbc,stroke:#e64a19,stroke-width:1px
    classDef governance fill:#fff9c4,stroke:#fbc02d,stroke-width:1px
    classDef utilities fill:#b3e5fc,stroke:#0288d1,stroke-width:1px
    classDef social fill:#f8bbd0,stroke:#c2185b,stroke-width:1px
    classDef domain fill:#d7ccc8,stroke:#5d4037,stroke-width:1px

    %% Core Module
    OPS[GEO-INFER-OPS]:::core

    %% Data Layer
    DATA[GEO-INFER-DATA]:::data
    SPACE[GEO-INFER-SPACE]:::data
    TIME[GEO-INFER-TIME]:::data
    API[GEO-INFER-API]:::utilities

    %% Analysis & Intelligence Layer
    ACT[GEO-INFER-ACT]:::analysis
    AI[GEO-INFER-AI]:::analysis
    AGENT[GEO-INFER-AGENT]:::analysis
    BAYES[GEO-INFER-BAYES]:::analysis
    MATH[GEO-INFER-MATH]:::analysis
    COG[GEO-INFER-COG]:::analysis
    SPM[GEO-INFER-SPM]:::analysis
    
    %% Simulation & Modeling
    SIM[GEO-INFER-SIM]:::analysis
    ANT[GEO-INFER-ANT]:::analysis
    
    %% Governance & Compliance
    SEC[GEO-INFER-SEC]:::governance
    NORMS[GEO-INFER-NORMS]:::governance
    REQ[GEO-INFER-REQ]:::governance

    %% Social & Community
    CIV[GEO-INFER-CIV]:::social
    PEP[GEO-INFER-PEP]:::social
    ORG[GEO-INFER-ORG]:::social
    COMMS[GEO-INFER-COMMS]:::social

    %% Applications
    APP[GEO-INFER-APP]:::presentation
    ART[GEO-INFER-ART]:::presentation

    %% Domain-Specific
    AG[GEO-INFER-AG]:::domain
    ECON[GEO-INFER-ECON]:::domain
    HEALTH[GEO-INFER-HEALTH]:::domain
    RISK[GEO-INFER-RISK]:::domain
    LOG[GEO-INFER-LOG]:::domain
    BIO[GEO-INFER-BIO]:::domain

    %% Operations & Documentation
    INTRA[GEO-INFER-INTRA]:::utilities
    GIT[GEO-INFER-GIT]:::utilities

    %% Core Orchestration
    OPS --> DATA
    OPS --> API
    OPS --> SEC
    OPS --> INTRA
    OPS --> GIT
    
    %% Data Layer Connections
    DATA <--> SPACE
    DATA <--> TIME
    DATA <--> API
    
    %% Spatial-Temporal to Analysis
    SPACE --> ACT
    SPACE --> AI
    SPACE --> SIM
    SPACE --> BAYES
    SPACE --> SPM
    TIME --> ACT
    TIME --> AI
    TIME --> SIM
    TIME --> BAYES
    TIME --> SPM
    
    %% Analysis Interconnections
    ACT <--> AI
    ACT <--> BAYES
    ACT <--> MATH
    ACT <--> COG
    ACT <--> AGENT
    ACT <--> SPM
    AI <--> BAYES
    AI <--> COG
    AI <--> AGENT
    AI <--> SPM
    AGENT <--> COG
    BAYES <--> MATH
    BAYES <--> SPM
    MATH <--> COG
    MATH <--> SPM
    
    %% Analysis to Simulation
    ACT --> ANT
    ACT --> SIM
    AI --> SIM
    AI --> ANT
    AGENT --> ANT
    AGENT --> SIM
    SIM <--> ANT
    BAYES --> SIM
    SPM --> SIM
    
    %% Governance Connections
    SEC --> DATA
    SEC --> API
    SEC --> APP
    NORMS <--> SEC
    NORMS --> SIM
    NORMS --> CIV
    REQ --> ACT
    REQ --> AI
    REQ --> SIM
    REQ --> APP
    REQ <--> NORMS
    REQ <--> SEC
    
    %% Social & Community Connections
    CIV <--> APP
    CIV <--> COMMS
    PEP <--> ORG
    PEP <--> COMMS
    ORG <--> COMMS
    CIV <--> ORG
    
    %% Applications Connections
    APP --> API
    APP <--> ART
    APP --> SPACE
    APP --> TIME
    APP --> ANT
    APP --> AI
    APP --> AGENT
    APP --> SIM
    APP --> NORMS
    APP --> SPM
    APP --> COMMS
    APP --> DATA
    APP --> INTRA
    
    %% Domain-Specific Connections
    AG --> SPACE
    AG --> TIME
    AG --> SIM
    AG --> APP
    AG --> SPM
    AG --> DATA

    ECON --> SPACE
    ECON --> TIME
    ECON --> SIM
    ECON --> APP
    ECON --> DATA
    ECON <--> AG

    HEALTH --> SPACE
    HEALTH --> TIME
    HEALTH --> SIM
    HEALTH --> APP
    HEALTH --> AI
    HEALTH --> AGENT
    HEALTH --> SPM
    HEALTH --> DATA
    HEALTH --> SEC
    HEALTH <--> RISK
    HEALTH <--> BIO

    RISK --> SPACE
    RISK --> TIME
    RISK --> SIM
    RISK --> AI
    RISK --> DATA
    RISK --> APP

    LOG --> SPACE
    LOG --> TIME
    LOG --> SIM
    LOG --> AI
    LOG --> DATA
    LOG --> APP

    BIO --> SPACE
    BIO --> TIME
    BIO --> SIM
    BIO --> AI
    BIO --> DATA
    BIO --> APP
    
    %% Documentation & Standards
    INTRA -.-> DATA
    INTRA -.-> SPACE
    INTRA -.-> TIME
    INTRA -.-> ACT
    INTRA -.-> AI
    INTRA -.-> AGENT
    INTRA -.-> BAYES
    INTRA -.-> MATH
    INTRA -.-> COG
    INTRA -.-> SIM
    INTRA -.-> ANT
    INTRA -.-> SEC
    INTRA -.-> NORMS
    INTRA -.-> REQ
    INTRA -.-> APP
    INTRA -.-> ART

    INTRA -.-> CIV
    INTRA -.-> PEP
    INTRA -.-> ORG
    INTRA -.-> COMMS
    INTRA -.-> AG
    INTRA -.-> ECON
    INTRA -.-> SPM
    INTRA -.-> HEALTH
    INTRA -.-> RISK
    INTRA -.-> LOG
    INTRA -.-> BIO
    
    %% Version Control Integrations
    GIT -.-> ALL
```

## Module Interaction Flow

```mermaid
flowchart TD
    classDef input fill:#bbf,stroke:#333,stroke-width:1px
    classDef process fill:#bfb,stroke:#333,stroke-width:1px
    classDef output fill:#fbb,stroke:#333,stroke-width:1px
    
    %% Data Collection & Processing
    A[External Data Sources]:::input --> B[GEO-INFER-DATA]
    B --> C{Data Processing}
    C --> D[GEO-INFER-SPACE]:::process
    C --> E[GEO-INFER-TIME]:::process
    
    %% Analysis Pipeline
    D & E --> F[Integrated Spatio-Temporal Data]
    F --> G[GEO-INFER-AI]:::process
    F --> H[GEO-INFER-ACT]:::process
    F --> X[GEO-INFER-SPM]:::process
    G & H & X --> I[Analytical Results]
    
    %% Simulation & Modeling
    I --> J[GEO-INFER-SIM]:::process
    J --> K[Scenario Models]
    I --> L[GEO-INFER-ANT]:::process
    L --> M[Complex System Models]
    I --> N[GEO-INFER-NORMS]:::process
    N --> O[Compliance & Regulatory Models]
    I --> P[GEO-INFER-BIO]:::process
    P --> Q[Biological System Models]
    I --> HEALTH_MOD[GEO-INFER-HEALTH]:::process
    B --> HEALTH_MOD
    HEALTH_MOD --> HEALTH_MOD_OUT[Health System Models]
    
    %% Presentation & Interaction
    K & M & O & Q & HEALTH_MOD_OUT --> R[Integrated Insights]
    R --> S[GEO-INFER-APP]:::output
    S --> T[User Interfaces]
    S --> U[GEO-INFER-CIV]:::output
    U --> V[Community Engagement]
    R --> ART_MOD[GEO-INFER-ART]:::output
    ART_MOD --> W_ART[Artistic Visualizations]
    
    %% Core Services
    W[GEO-INFER-OPS]:::process --> B & G & S
    X[GEO-INFER-API]:::process --> T & U
    Y[GEO-INFER-SEC]:::process -.-> B & X & S & U
    Y -.-> HEALTH_MOD
    Z[GEO-INFER-INTRA]:::process -.-> All
    COMMS_MOD[GEO-INFER-COMMS]:::process --> S
```

## Technology Stack Architecture

```mermaid
graph BT
    classDef storage fill:#f9f,stroke:#333,stroke-width:1px
    classDef processing fill:#bbf,stroke:#333,stroke-width:1px
    classDef serving fill:#bfb,stroke:#333,stroke-width:1px
    classDef security fill:#fbb,stroke:#333,stroke-width:1px
    classDef ui fill:#fbf,stroke:#333,stroke-width:1px

    %% Data Storage Layer
    PG[(PostgreSQL)]:::storage
    POSTGIS[(PostGIS)]:::storage
    MINIO[(MinIO)]:::storage
    TIMESCALEDB[(TimescaleDB)]:::storage
    REDIS[(Redis)]:::storage

    %% Data Processing Layer
    SPARK[Apache Spark]:::processing
    KAFKA[Kafka]:::processing
    AIRFLOW[Airflow]:::processing
    PYTHON[Python Ecosystem]:::processing
    R[R Statistical]:::processing
    TENSOR[TensorFlow/PyTorch]:::processing

    %% API & Serving Layer
    FASTAPI[FastAPI]:::serving
    GRAPHQL[GraphQL]:::serving
    OGC[OGC Services]:::serving
    MAPSERVER[MapServer]:::serving

    %% Security Layer
    KEYCLOAK[Keycloak]:::security
    VAULT[HashiCorp Vault]:::security
    CERT[Cert Manager]:::security

    %% UI Layer
    REACT[React]:::ui
    LEAFLET[Leaflet/Mapbox]:::ui
    DECK[deck.gl]:::ui
    D3[D3.js]:::ui

    %% Infrastructure
    K8S[Kubernetes]:::processing
    DOCKER[Docker]:::processing
    ISTIO[Istio]:::security

    %% Connections
    PG --- POSTGIS
    PG --- TIMESCALEDB
    
    %% Storage to Processing
    POSTGIS --> SPARK
    MINIO --> SPARK
    TIMESCALEDB --> SPARK
    REDIS --> KAFKA
    
    %% Processing interconnections
    SPARK <--> KAFKA
    SPARK <--> AIRFLOW
    KAFKA <--> AIRFLOW
    PYTHON <--> SPARK
    R <--> SPARK
    TENSOR <--> PYTHON
    
    %% Processing to Serving
    PYTHON --> FASTAPI
    SPARK --> FASTAPI
    PYTHON --> GRAPHQL
    POSTGIS --> OGC
    POSTGIS --> MAPSERVER
    
    %% Security crosscutting
    KEYCLOAK -.-> FASTAPI
    KEYCLOAK -.-> GRAPHQL
    KEYCLOAK -.-> OGC
    VAULT -.-> FASTAPI
    CERT -.-> FASTAPI
    CERT -.-> GRAPHQL
    
    %% Serving to UI
    FASTAPI --> REACT
    GRAPHQL --> REACT
    OGC --> LEAFLET
    MAPSERVER --> LEAFLET
    FASTAPI --> DECK
    LEAFLET --> D3
    DECK --> D3
    
    %% Infrastructure
    K8S --- DOCKER
    K8S --- ISTIO
    ISTIO -.-> KEYCLOAK

    %% Subgraphs for organization
    subgraph "Storage Layer"
        PG
        POSTGIS
        MINIO
        TIMESCALEDB
        REDIS
    end
    
    subgraph "Processing Layer"
        SPARK
        KAFKA
        AIRFLOW
        PYTHON
        R
        TENSOR
        K8S
        DOCKER
        ISTIO
    end
    
    subgraph "API & Serving Layer"
        FASTAPI
        GRAPHQL
        OGC
        MAPSERVER
    end
    
    subgraph "Security Layer"
        KEYCLOAK
        VAULT
        CERT
    end
    
    subgraph "UI Layer"
        REACT
        LEAFLET
        DECK
        D3
    end
```

## Project Structure 📂

Each module generally follows this standardized structure, though some may include additional directories specific to their domain or function (e.g., `etl/`, `storage/`, `repos/`).
```
MODULE_NAME/
├── config/               # Configuration files
├── docs/                 # Documentation
├── examples/             # Example applications and use cases
├── src/                  # Source code
│   └── module_package/   # Main package
│       ├── api/          # API definitions
│       ├── core/         # Core functionality
│       ├── models/       # Data models
│       └── utils/        # Utility functions
└── tests/                # Test suite
```

## Technology Stack

### **Core Technologies **

- 🐍 **Python Ecosystem** 
  - [NumPy](https://numpy.org/) & [SciPy](https://scipy.org/) with GPU acceleration
  - [Pandas](https://pandas.pydata.org/) & [GeoPandas](https://geopandas.org/) with Dask integration
  - [PyTorch](https://pytorch.org/) & [TensorFlow](https://www.tensorflow.org/) with quantum extensions
  - [Dask](https://dask.org/) for distributed computing at petabyte scale

- 🗄️ **Data Storage** 
  - [PostgreSQL](https://www.postgresql.org/) with [PostGIS](https://postgis.net/) (clustered, sharded)
  - [TimescaleDB](https://www.timescale.com/) for real-time time-series (2.3PB/month)
  - [MinIO](https://min.io/) distributed object storage (S3-compatible)
  - [Redis](https://redis.io/) cluster for sub-millisecond caching

- 🌐 **API & Services** 
  - [FastAPI](https://fastapi.tiangolo.com/) with async/await (1B+ requests/month)
  - [GraphQL](https://graphql.org/) with federation and subscriptions
  - [gRPC](https://grpc.io/) for high-performance microservices
  - [Apache Kafka](https://kafka.apache.org/) for event streaming

- 🖥️ **Frontend** 
  - [React 18](https://reactjs.org/) with Concurrent Features
  - [Leaflet](https://leafletjs.com/) & [Mapbox](https://www.mapbox.com/) with WebGL
  - [D3.js](https://d3js.org/) & [Observable Plot](https://observablehq.com/plot/) for visualization
  - [deck.gl](https://deck.gl/) for large-scale 3D visualizations

- 🚢 **DevOps** 
  - [Docker](https://www.docker.com/) with multi-stage builds
  - [Kubernetes](https://kubernetes.io/) with Istio service mesh
  - [GitHub Actions](https://github.com/features/actions) with advanced workflows
  - [Terraform](https://www.terraform.io/) for infrastructure as code
  - [ArgoCD](https://argo-cd.readthedocs.io/) for GitOps deployments

## 👥 **Contributing & Community **

### **💡 Ways to Contribute**

#### **🔧 Technical Contributions**
- **Code contributions**: Bug fixes, features, optimizations
- **Documentation**: Tutorials, API docs, examples
- **Testing**: Unit tests, integration tests, performance benchmarks
- **Infrastructure**: DevOps, monitoring, security improvements

#### **🎓 Knowledge Sharing**
- **Blog posts**: Technical deep-dives, case studies
- **Conference talks**: Present at GIS, AI, and domain conferences
- **Workshops**: Hands-on training sessions
- **Mentorship**: Guide new contributors and users

#### **🌍 Community Building**
- **Local meetups**: Organize regional GEO-INFER groups
- **Translation**: Localize documentation to new languages
- **Outreach**: Introduce GEO-INFER to new communities
- **Partnerships**: Connect academic and industry collaborations

### **📋 Contribution Guidelines**

**Quick Start for Contributors**:
1. **Join Discord**: [discord.activeinference.institute](https://discord.activeinference.institute/)
2. **Read Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Choose First Issue**: Look for "good first issue" labels
4. **Set up Development**: Follow setup instructions
5. **Submit PR**: Use our PR template and guidelines

### **🤝 Partnership Opportunities**

**Academic Partnerships**:
- **Research collaborations**: Joint research projects and grants
- **Curriculum integration**: University course development
- **Student programs**: Internships and thesis projects
- **Faculty exchange**: Visiting researcher programs

**Industry Partnerships**:
- **Technology integration**: API partnerships and integrations
- **Joint solutions**: Co-developed products and services
- **Training programs**: Custom training
- **Consulting services**: Implementation and optimization support

**Government & NGO Partnerships**:
- **Capacity building**: Training programs for developing countries
- **Policy development**: Evidence-based policy recommendations
- **Disaster response**: Emergency response system deployment
- **Environmental monitoring**: Conservation and climate programs

## 📄 **License & Legal**

This project is licensed under the **Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0)**. See the [LICENSE](LICENSE) file for details.

**Contact**: blanket@activeinference.institute (use subject "GEO-INFER")

---

**GEO-INFER**: *Transforming spatial data into actionable intelligence for a better world.*

[![Get Started](https://img.shields.io/badge/Get%20Started-Interactive%20Tutorial-brightgreen?style=for-the-badge)](https://learn.geo-infer.org/quickstart)
[![Join Community](https://img.shields.io/badge/Join%20Community-Discord-7289DA?style=for-the-badge)](https://discord.activeinference.institute/)
