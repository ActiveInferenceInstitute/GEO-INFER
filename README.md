# 🌍 GEO-INFER Framework

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/geo-infer/geo-infer/pulls)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289DA.svg)](https://discord.activeinference.institute/)
[![H3 Version](https://img.shields.io/badge/H3-v4.0+-blue.svg)](https://h3geo.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org/)

<div align="center">
  <h3>Geospatial Inference Framework</h3>
  <p><em>Implementing Active Inference principles for regional, ecological, civic, and commercial applications</em></p>
  <br>
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#-module-overview">📦 Modules</a> •
  <a href="#-use-cases">🎯 Use Cases</a> •
  <a href="#-documentation">📚 Docs</a> •
  <a href="#-contributing">👥 Contribute</a> •
  <a href="./PAI.md">🤖 PAI</a> •
  <a href="./AGENTS.md">🧠 Agents</a> •
  <a href="./SKILL.md">🧩 Skill</a> •
  <a href="./CLAUDE.md">📋 Claude</a> •
  <a href="./TODO.md">📝 TODO</a>
</div>

---

## 🌟 What is GEO-INFER?

**GEO-INFER** is a geospatial inference framework that implements Active Inference principles for spatial-temporal problems. The framework provides **44 specialized modules** organized into categories with defined dependencies and data flow patterns.

### ✨ Key Features

- **🗺️ Spatial Analysis**: H3 v4 spatial indexing and geospatial processing
- **🧠 Active Inference**: Mathematical foundations for perception-action loops (free energy minimization, Bayesian inference, perception-action loops)
- **🔄 Data Processing Pipelines**: Validation, quality control, and ETL workflows
- **🧩 Modular Architecture**: 44 specialized modules with clear dependencies
- **🧪 Testing**: 434 test files with ~3,000+ tests across all modules
- **📚 Documentation**: Standardized documentation with integration guides

### 📊 Codebase at a Glance

| Metric | Value |
|--------|-------|
| **Modules** | 44 specialized packages |
| **Source Files** | 860 files, 297,360 lines |
| **Test Files** | 422 files, ~87,000+ lines |
| **Tests** | ~3,000+ passing |
| **Min Tests/Module** | 4 test files (every module) |
| **Package Standard** | PEP 8 lowercase naming across all 44 packages (`geo_infer_<module>`) |

## 🚀 Quick Start

### ⚡ Get Started in 3 Steps

```bash
# Step 1: Clone and enter the repository
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER

# Step 2: Install core modules (choose what you need)
uv pip install -e ./GEO-INFER-MATH    # Mathematical foundations
uv pip install -e ./GEO-INFER-SPACE   # Spatial analysis (H3 v4)
uv pip install -e ./GEO-INFER-ACT     # Active inference

# Step 3: Run your first analysis
python -c "
from geo_infer_space import SpatialIndexingInterface
from geo_infer_act import ActiveInferenceModel

# Create your first spatial analysis
indexer = SpatialIndexingInterface()
cell = indexer.latlng_to_cell(37.7749, -122.4194, 9)
model = ActiveInferenceModel(model_type='categorical')

print('\U0001f389 GEO-INFER is ready!')
print(f'H3 cell: {cell}')
print('\U0001f4da Check GEO-INFER-INTRA/docs/ for documentation')
"
```

### 📋 Prerequisites

- **Python**: 3.11+
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (fast, reliable Python package installer)
- **Git**: For cloning and version control
- **Optional**: Docker for containerized deployment

### 🎯 First Steps by Use Case

| I want to... | Start with these modules | Example command |
|-------------|-------------------------|-----------------|
| **Analyze spatial data** | `MATH`, `SPACE` | `uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE` |
| **Build AI models** | `MATH`, `AI`, `DATA` | `uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-AI ./GEO-INFER-DATA` |
| **Process sensor data** | `IOT`, `DATA`, `TIME` | `uv pip install -e ./GEO-INFER-IOT ./GEO-INFER-DATA ./GEO-INFER-TIME` |
| **Design governance systems** | `METAGOV`, `ORG`, `NORMS` | `uv pip install -e ./GEO-INFER-METAGOV ./GEO-INFER-ORG ./GEO-INFER-NORMS` |
| **Create web applications** | `API`, `APP`, `SPACE` | `uv pip install -e ./GEO-INFER-API ./GEO-INFER-APP ./GEO-INFER-SPACE` |

## 📦 Module Overview

GEO-INFER provides **44 specialized modules** organized into clear categories. Each module follows standardized documentation with working examples and integration guides.

### 🧠 Core Analytical Modules

| Module | Purpose | Status |
|--------|---------|--------|
| **MATH** | Mathematical foundations, statistics, optimization | ✅ Beta |
| **ACT** | Active Inference modeling and belief updates | ✅ Beta |
| **BAYES** | Bayesian inference (GP, MCMC, model comparison) | ✅ Beta |
| **AI** | Machine learning and neural networks | ✅ Beta |
| **COG** | Cognitive modeling and spatial cognition | ✅ Beta |
| **AGENT** | Intelligent agents and autonomous systems | ✅ Beta |
| **SPM** | Statistical mapping and spatial statistics | 🟡 Alpha |

### 🗺️ Spatial-Temporal Modules

| Module | Purpose | Status |
|--------|---------|--------|
| **SPACE** | H3 v4 spatial indexing and geospatial analysis | ✅ **FULLY MIGRATED** |
| **TIME** | Temporal methods and time series analysis | ✅ Beta |
| **IOT** | IoT sensor networks and real-time data | ✅ Beta |

### 💾 Infrastructure Modules

| Module | Purpose | Status |
|--------|---------|--------|
| **DATA** | ETL processes and data pipeline management | ✅ Beta |
| **API** | REST/GraphQL services and external integration | ✅ Beta |
| **SEC** | Security frameworks and access control | 🟡 Alpha |
| **OPS** | System orchestration and monitoring | 🟡 Alpha |
| **METAGOV** | Meta-governance and organizational governance methods | 🟡 Alpha |

### 🎯 Domain Applications

| Category | Key Modules | Status |
|----------|-------------|--------|
| **Agriculture** | AG (precision farming, crop monitoring) | ✅ Beta |
| **Health** | HEALTH (epidemiology, healthcare access) | ✅ Beta |
| **Economics** | ECON (market analysis, policy modeling) | ✅ Beta |
| **Risk** | RISK (insurance, hazard assessment) | 🟡 Alpha |
| **Logistics** | LOG (supply chains, route optimization) | ✅ Beta |
| **Biology** | BIO (spatial omics, ecological modeling) | ✅ Beta |
| **Climate** | CLIMATE (climate modeling, adaptation) | ✅ Beta |
| **Energy** | ENERGY (renewables, grid optimization) | 🟡 Alpha |
| **Water** | WATER (hydrology, water quality) | 🟡 Alpha |
| **Transport** | TRANSPORT (traffic, urban mobility) | 🟡 Alpha |
| **Forest** | FOREST (forestry, deforestation detection) | ✅ Beta |
| **Marine** | MARINE (ocean, coastal management) | 🟡 Alpha |
| **Emergency** | EMERGENCY (disaster response, evacuation) | 🟡 Alpha |
| **Education** | EDU (learning, curriculum design) | 🟡 Alpha |

### 🤖 Agent Documentation

All modules have `AGENTS.md` files documenting:

- Agent capabilities and integration patterns
- Implementation status (✅ Implemented / 🔮 Planned)
- Code examples for agent integration
- Framework support vs domain applications

See [AGENTS.md](./AGENTS.md) for the complete multi-agent systems architecture.

### 👥 Community & Applications

| Module | Purpose | Status |
|--------|---------|--------|
| **CIV** | Civic engagement and participatory mapping | 🟡 Alpha |
| **APP** | User interfaces and dashboards | ✅ Beta |
| **ART** | Artistic expression and visualization | ✅ Beta |
| **PLACE** | Place-based analysis and regional insights | ✅ **FULLY MIGRATED** |

## 📚 Documentation & Resources

### 🎯 Getting Started Guides

| Resource | Description | Location |
|----------|-------------|----------|
| **Quick Start Tutorial** | 15-minute introduction to GEO-INFER | `GEO-INFER-EXAMPLES/examples/basic_tutorial.md` |
| **Module Integration Guide** | Cross-module integration patterns | `GEO-INFER-INTRA/docs/guides/MODULE_INTEGRATION_GUIDE.md` |
| **Environmental Monitoring** | Specialized environmental workflows | `GEO-INFER-INTRA/docs/guides/ENVIRONMENTAL_MONITORING_INTEGRATION.md` |
| **API Documentation** | Complete API reference | `GEO-INFER-INTRA/docs/api/` |

### 📖 Documentation Standards

| Resource | Description | Status |
|----------|-------------|--------|
| **Documentation Standards** | Comprehensive contribution guidelines | ✅ **COMPLETE** |
| **Module Templates** | Standardized YAML front matter templates | ✅ **AVAILABLE** |
| **Integration Guides** | Cross-module workflow tutorials | ✅ **ESTABLISHED** |
| **Code Examples** | Working, tested code samples | ✅ **VERIFIED** |

### 🧪 Testing & Quality

| Resource | Description | Command |
|----------|-------------|---------|
| **Unified Test Suite** | Run all tests across modules | `uv run python GEO-INFER-TEST/run_unified_tests.py` |
| **Module-Specific Tests** | Test individual modules | `uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH` |
| **Integration Tests** | Cross-module integration testing | `uv run python GEO-INFER-TEST/run_unified_tests.py --category integration` |
| **Performance Benchmarks** | Performance validation | `uv run python GEO-INFER-TEST/run_unified_tests.py --category performance` |

### 🔗 Key Resources

- **📋 Module Index**: Complete module overview with status and dependencies
- **🎨 Integration Examples**: Integration patterns and use cases
- **📚 API Documentation**: API references and schemas
- **🔧 Development Standards**: Coding guidelines and best practices
- **🧪 Quality Assurance**: Testing frameworks and validation procedures

## 🏗️ Architecture Overview

| Category                     | Modules                                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **🧠 Analytical Core**       | [ACT](./GEO-INFER-ACT/), [BAYES](./GEO-INFER-BAYES/), [AI](./GEO-INFER-AI/), [MATH](./GEO-INFER-MATH/), [COG](./GEO-INFER-COG/), [AGENT](./GEO-INFER-AGENT/), [SPM](./GEO-INFER-SPM/) |
| **🗺️ Spatial-Temporal**     | [SPACE](./GEO-INFER-SPACE/), [TIME](./GEO-INFER-TIME/), [IOT](./GEO-INFER-IOT/)                                                                                                       |
| **💾 Data Management**       | [DATA](./GEO-INFER-DATA/), [API](./GEO-INFER-API/)                                                                                                           |
| **🔒 Security & Governance** | [SEC](./GEO-INFER-SEC/), [NORMS](./GEO-INFER-NORMS/), [REQ](./GEO-INFER-REQ/), [METAGOV](./GEO-INFER-METAGOV/)                                                                                |
| **🧪 Simulation & Modeling** | [SIM](./GEO-INFER-SIM/), [ANT](./GEO-INFER-ANT/)                                                                                                             |
| **👥 People & Community**    | [CIV](./GEO-INFER-CIV/), [PEP](./GEO-INFER-PEP/), [ORG](./GEO-INFER-ORG/), [COMMS](./GEO-INFER-COMMS/)                                                       |
| **🖥️ Applications**         | [APP](./GEO-INFER-APP/), [ART](./GEO-INFER-ART/)                                                                                                             |
| **🏢 Domain-Specific**       | [AG](./GEO-INFER-AG/), [HEALTH](./GEO-INFER-HEALTH/), [ECON](./GEO-INFER-ECON/), [RISK](./GEO-INFER-RISK/), [LOG](./GEO-INFER-LOG/), [BIO](./GEO-INFER-BIO/), [CLIMATE](./GEO-INFER-CLIMATE/), [ENERGY](./GEO-INFER-ENERGY/), [WATER](./GEO-INFER-WATER/), [TRANSPORT](./GEO-INFER-TRANSPORT/), [FOREST](./GEO-INFER-FOREST/), [MARINE](./GEO-INFER-MARINE/), [EMERGENCY](./GEO-INFER-EMERGENCY/), [EDU](./GEO-INFER-EDU/) |
| **📍 Place-Based**           | [PLACE](./GEO-INFER-PLACE/)                                                                                                                                                                      |
| **⚙️ Operations**            | [OPS](./GEO-INFER-OPS/), [INTRA](./GEO-INFER-INTRA/), [GIT](./GEO-INFER-GIT/), [TEST](./GEO-INFER-TEST/), [EXAMPLES](./GEO-INFER-EXAMPLES/)                                                    |

## Architecture

 Overview

```mermaid
graph TB
    %% Note: no explicit styling; keep dark-mode compatible

    %% Core Analytical Layer
    MATH["GEO-INFER-MATH<br/>Mathematical Foundations"]
    BAYES["GEO-INFER-BAYES<br/>Bayesian Inference"]
    ACT["GEO-INFER-ACT<br/>Active Inference"]
    AI["GEO-INFER-AI<br/>Artificial Intelligence"]
    COG["GEO-INFER-COG<br/>Cognitive Modeling"]
    AGENT["GEO-INFER-AGENT<br/>Intelligent Agents"]
    SPM["GEO-INFER-SPM<br/>Statistical Mapping"]

    %% Spatial-Temporal Layer
    SPACE["GEO-INFER-SPACE<br/>Spatial Methods H3 v4"]
    TIME["GEO-INFER-TIME<br/>Temporal Methods"]
    IOT["GEO-INFER-IOT<br/>IoT Integration"]

    %% Data Management Layer
    DATA["GEO-INFER-DATA<br/>Data Management"]
    API["GEO-INFER-API<br/>API Services"]

    %% Operations Layer
    OPS["GEO-INFER-OPS<br/>Orchestration"]
    SEC["GEO-INFER-SEC<br/>Security"]
    INTRA["GEO-INFER-INTRA<br/>Documentation"]
    GIT["GEO-INFER-GIT<br/>Version Control"]
    TEST["GEO-INFER-TEST<br/>Quality Assurance"]

    %% Domain-Specific Layer
    AG["GEO-INFER-AG<br/>Agriculture"]
    HEALTH["GEO-INFER-HEALTH<br/>Health Applications"]
    ECON["GEO-INFER-ECON<br/>Economics"]
    RISK["GEO-INFER-RISK<br/>Risk Management"]
    LOG["GEO-INFER-LOG<br/>Logistics"]
    BIO["GEO-INFER-BIO<br/>Bioinformatics"]

    %% Application Layer
    APP["GEO-INFER-APP<br/>User Interfaces"]
    ART["GEO-INFER-ART<br/>Artistic Expression"]
    PLACE["GEO-INFER-PLACE<br/>Place-Based Analysis"]

    %% Simulation Layer
    SIM["GEO-INFER-SIM<br/>Simulation"]
    ANT["GEO-INFER-ANT<br/>Complex Systems"]

    %% People & Community Layer
    CIV["GEO-INFER-CIV<br/>Civic Engagement"]
    PEP["GEO-INFER-PEP<br/>People Management"]
    ORG["GEO-INFER-ORG<br/>Organizations"]
    COMMS["GEO-INFER-COMMS<br/>Communications"]

    %% Governance Layer
    NORMS["GEO-INFER-NORMS<br/>Compliance"]
    REQ["GEO-INFER-REQ<br/>Requirements"]
    METAGOV["GEO-INFER-METAGOV<br/>Meta-Governance"]

    %% Examples Layer
    EXAMPLES["GEO-INFER-EXAMPLES<br/>Cross-Module Demos"]

    %% Core Dependencies
    MATH --> BAYES
    MATH --> ACT
    MATH --> AI
    MATH --> SPM
    BAYES --> ACT
    AI --> AGENT
    ACT --> AGENT
    COG --> AGENT

    %% Spatial Dependencies
    SPACE --> AG
    SPACE --> HEALTH
    SPACE --> ECON
    SPACE --> RISK
    SPACE --> LOG
    SPACE --> BIO
    SPACE --> PLACE
    TIME --> AG
    TIME --> HEALTH
    TIME --> ECON
    TIME --> SIM
    IOT --> SPACE
    IOT --> TIME

    %% Data Dependencies
    DATA --> SPACE
    DATA --> TIME
    DATA --> AI
    DATA --> AG
    DATA --> HEALTH
    DATA --> ECON
    API --> APP
    API --> ART

    %% Operations Dependencies
    OPS --> DATA
    OPS --> SEC
    SEC --> DATA
    SEC --> API
    INTRA --> COMMS
    GIT --> OPS
    TEST --> OPS

    %% Domain Dependencies
    AG --> APP
    HEALTH --> APP
    ECON --> APP
    RISK --> APP
    LOG --> ECON
    BIO --> HEALTH

    %% Simulation Dependencies
    SIM --> SPACE
    SIM --> TIME
    SIM --> AI
    ANT --> ACT
    ANT --> SIM

    %% People Dependencies
    CIV --> APP
    PEP --> ORG
    ORG --> COMMS
    COMMS --> INTRA

    %% Governance Dependencies
    NORMS --> SEC
    REQ --> NORMS
    REQ --> SEC

    %% Examples Dependencies
    EXAMPLES --> APP
    EXAMPLES --> SPACE
    EXAMPLES --> TIME
```

## 📊 Complete Module Dependencies Matrix

| Module | Core Dependencies | Optional Dependencies | Provides Services To | Data Flow Direction | Status | H3 v4 Status |
|--------|------------------|--------------------|-------------------|-------------------|---------|---------------|
| **OPS** | - | SEC | ALL modules | → All | Beta | ✅ Updated |
| **DATA** | OPS, SEC | - | ALL modules | → All | Alpha | ✅ Updated |
| **SPACE** | DATA, MATH | TIME, AI, IOT | AG, HEALTH, SIM, APP, ART, PLACE, LOG, RISK, BIO, ECON | → Domain/App | Beta | ✅ **FULLY MIGRATED** |
| **TIME** | DATA, MATH | SPACE, AI, IOT | AG, HEALTH, ECON, SIM, LOG, RISK, BIO | → Domain/Analytics | Alpha | ⏳ Not Applicable |
| **IOT** | SPACE, DATA | BAYES, TIME, AI | All sensor-based modules | → Sensor/Real-time | Beta | ✅ Updated |
| **AI** | DATA, SPACE | TIME, AGENT | All analytical modules | → Analytics/Prediction | Gamma | ⏳ Planned |
| **ACT** | MATH, BAYES | AI, AGENT, SIM | AGENT, SIM, decision systems | → Inference/Decision | Beta | ✅ Updated |
| **BAYES** | MATH | SPACE, TIME | ACT, AI, statistical modules | → Statistical/Inference | Beta | ✅ Updated |
| **MATH** | - | - | ALL analytical modules | → All analytics | Beta | ✅ Updated |
| **API** | All modules | - | External systems, APP | ↔ External | Beta | ✅ Updated |
| **APP** | API, SPACE | All modules | End users | ← All modules | Beta | ✅ Updated |
| **AGENT** | ACT, AI | SPACE, TIME, SIM | SIM, autonomous systems | ↔ Agent systems | Beta | ✅ Updated |
| **SIM** | SPACE, TIME | AI, AGENT, ACT | Domain modules, decision support | ↔ Simulation systems | Alpha | ⏳ Planned |
| **AG** | SPACE, TIME, DATA | AI, ECON, SIM | APP, ECON, food systems | ↔ Agricultural systems | Beta | ✅ Updated |
| **HEALTH** | SPACE, TIME, DATA | AI, RISK, BIO, SPM | APP, policy makers | ↔ Health systems | Beta | ✅ Updated |
| **ECON** | SPACE, TIME, DATA | AI, AG, SIM | Policy makers, RISK | ↔ Economic systems | Beta | ✅ Updated |
| **ANT** | ACT, SIM | AI, AGENT | SIM, complex systems | ↔ Complex systems | Alpha | ⏳ Planned |
| **ART** | SPACE, APP | AI, TIME | APP, visualization | ← Artistic/Creative | Beta | ✅ Updated |
| **BIO** | SPACE, TIME, DATA | AI, HEALTH | HEALTH, research | ↔ Biological systems | Beta | ✅ Updated |
| **COG** | SPACE, AI | ACT, AGENT | AGENT, human factors | → Cognitive modeling | Beta | ✅ Updated |
| **COMMS** | INTRA, APP | ALL modules | External stakeholders | ← All modules | Beta | ✅ Updated |
| **GIT** | OPS | - | All development | → Version control | Beta | ✅ Updated |
| **INTRA** | - | ALL modules | Documentation, standards | ← All modules | Beta | ✅ Updated |
| **LOG** | SPACE, TIME, DATA | AI, SIM | ECON, operations | ↔ Logistics systems | Beta | ✅ Updated |
| **NORMS** | SPACE, DATA | REQ, SEC | All compliance | → Regulatory/Ethics | Beta | ✅ Updated |
| **ORG** | PEP, COMMS | CIV, NORMS | Governance systems | ↔ Organizational | Beta | ✅ Updated |
| **PEP** | ORG, COMMS | CIV | HR, community | ↔ People management | Beta | ✅ Updated |
| **REQ** | NORMS, SEC | ALL modules | System specifications | → Requirements | Beta | ✅ Updated |
| **RISK** | SPACE, TIME, DATA | AI, HEALTH, ECON | Decision support | ↔ Risk assessment | Beta | ✅ Updated |
| **SEC** | - | ALL modules | Security services | → All modules | Alpha | ✅ Updated |
| **SPM** | MATH, SPACE | TIME, BAYES | Statistical analysis | → Statistical mapping | Alpha | ✅ Updated |
| **TEST** | ALL modules | - | Quality assurance | ← All modules | Alpha | ✅ Updated |
| **EXAMPLES** | All modules | - | New users, developers | ← All modules (demo only) | Beta | ✅ Updated |
| **PLACE** | SPACE, TIME, DATA, ALL | - | Regional analyses, place-based insights | ↔ Place-based systems | Beta | ✅ **FULLY MIGRATED** |
| **CIV** | SPACE, APP | COMMS, ORG | Community engagement | ↔ Civic systems | Alpha | ✅ Updated |
| **METAGOV** | ORG, SEC, NORMS | COMMS, REQ | Meta-governance & organizational governance | → Governance/Meta-organization | Alpha | ✅ Updated |
| **CLIMATE** | SPACE, TIME, BAYES, ACT | AG, HEALTH, RISK | Climate modeling, weather analysis, climate change | → Climate/Environmental | Beta | ✅ Updated |
| **ENERGY** | SPACE, TIME, ECON, RISK | IOT, AGENT | Energy systems, renewable optimization, grid | → Energy/Sustainability | Alpha | ✅ Updated |
| **WATER** | SPACE, TIME, DATA, RISK | AG, HEALTH | Water resources, hydrology, water quality | → Water/Resource | Alpha | ✅ Updated |
| **TRANSPORT** | SPACE, TIME, LOG, AGENT | CIV, IOT | Transportation systems, urban mobility | → Transport/Mobility | Alpha | ✅ Updated |
| **EDU** | SPACE, TIME, CIV, HEALTH | ECON | Educational systems, school accessibility | → Education/Social | Alpha | ✅ Updated |
| **EMERGENCY** | SPACE, TIME, RISK, AGENT, IOT | ANT | Emergency management, disaster response | → Emergency/Safety | Alpha | ✅ Updated |

### Legend

- **→** : Provides data/services to  
- **←** : Consumes data/services from  
- **↔** : Bidirectional data exchange
- **Status**: Alpha (Early Development), Beta (Production Ready), Gamma (Planned)

## 🔄 Data Flow Architecture

```mermaid
flowchart TD
    %% Note: no explicit styling; keep dark-mode compatible

    %% Data Sources
    RS["Remote Sensing Data"]
    IOT["IoT Sensor Streams"]
    CSV["Tabular Datasets"]
    OSM["OpenStreetMap Data"]
    CGD["Crowdsourced Geodata"]
    API["External APIs"]
    SENSOR["Environmental Sensors"]
    
    %% Data Processing Layer
    DATA["GEO-INFER-DATA<br/>Data Management & ETL"]
    SPACE["GEO-INFER-SPACE<br/>Spatial Processing H3 v4"]
    TIME["GEO-INFER-TIME<br/>Temporal Processing"]
    SEC["GEO-INFER-SEC<br/>Security & Privacy"]

    %% Analytical Layer
    MATH["GEO-INFER-MATH<br/>Mathematical Foundations"]
    BAYES["GEO-INFER-BAYES<br/>Bayesian Inference"]
    ACT["GEO-INFER-ACT<br/>Active Inference"]
    AI["GEO-INFER-AI<br/>Machine Learning"]
    SPM["GEO-INFER-SPM<br/>Statistical Mapping"]

    %% Domain-Specific Analysis
    AG["GEO-INFER-AG<br/>Agricultural Analysis"]
    HEALTH["GEO-INFER-HEALTH<br/>Health Applications"]
    ECON["GEO-INFER-ECON<br/>Economic Modeling"]
    RISK["GEO-INFER-RISK<br/>Risk Assessment"]
    LOG["GEO-INFER-LOG<br/>Logistics Optimization"]
    BIO["GEO-INFER-BIO<br/>Bioinformatics"]

    %% Simulation & Modeling
    SIM["GEO-INFER-SIM<br/>Simulation Engine"]
    ANT["GEO-INFER-ANT<br/>Complex Systems"]
    AGENT["GEO-INFER-AGENT<br/>Intelligent Agents"]

    %% Application Layer
    APP["GEO-INFER-APP<br/>User Interfaces"]
    ART["GEO-INFER-ART<br/>Artistic Expression"]
    PLACE["GEO-INFER-PLACE<br/>Place-Based Analysis"]

    %% Output Layer
    API_OUT["API Services"]
    DASH["Dashboards & Reports"]
    MAPS["Interactive Maps"]
    MODELS["Trained Models"]
    INSIGHTS["Analytical Insights"]

    %% Data Flow Connections
    RS --> DATA
    IOT --> DATA
    CSV --> DATA
    OSM --> DATA
    CGD --> DATA
    API --> DATA
    SENSOR --> DATA

    DATA --> SPACE
    DATA --> TIME
    DATA --> SEC

    SPACE --> MATH
    SPACE --> BAYES
    SPACE --> ACT
    SPACE --> AI
    SPACE --> SPM

    TIME --> MATH
    TIME --> BAYES
    TIME --> ACT
    TIME --> AI

    MATH --> BAYES
    MATH --> ACT
    MATH --> AI
    MATH --> SPM

    BAYES --> ACT
    BAYES --> AI
    BAYES --> SPM

    ACT --> AI
    ACT --> AGENT

    AI --> AG
    AI --> HEALTH
    AI --> ECON
    AI --> RISK
    AI --> LOG
    AI --> BIO

    SPACE --> AG
    SPACE --> HEALTH
    SPACE --> ECON
    SPACE --> RISK
    SPACE --> LOG
    SPACE --> BIO
    SPACE --> PLACE

    TIME --> AG
    TIME --> HEALTH
    TIME --> ECON
    TIME --> RISK
    TIME --> LOG
    TIME --> BIO
    TIME --> SIM

    AG --> APP
    HEALTH --> APP
    ECON --> APP
    RISK --> APP
    LOG --> APP
    BIO --> APP
    PLACE --> APP

    SIM --> APP
    ANT --> APP
    AGENT --> APP

    APP --> API_OUT
    APP --> DASH
    APP --> MAPS
    APP --> MODELS
    APP --> INSIGHTS

    ART --> MAPS
    ART --> INSIGHTS
```

## 🔧 Core Modules (Enhanced)

| **Module Name**     | **Purpose**                                                                                        | **Input Types** | **Output Types** | **Dependencies** | **Status** | **H3 v4 Status** |
| ------------------- | -------------------------------------------------------------------------------------------------- | --------------- | ---------------- | ---------------- | ---------- | ---------------- |
| **GEO-INFER-ACT**   | [Active Inference modeling for nested and interacting systems](./GEO-INFER-ACT/README.md) | Observations, beliefs, policies, generative models | Belief updates, action selections, free energy estimates | MATH, BAYES | Alpha | ✅ Updated |
| **GEO-INFER-AG**    | [Agricultural methods and farming applications](./GEO-INFER-AG/README.md) | Satellite imagery, soil data, weather data, field boundaries | Yield predictions, crop health maps, precision agriculture recommendations | SPACE, TIME, DATA | Alpha | ✅ Updated |
| **GEO-INFER-AI**    | [Artificial Intelligence and Machine Learning for geospatial workflows](./GEO-INFER-AI/README.md) | Imagery, spatial features, training labels, time-series data | Trained models, predictions, classifications, forecasts | DATA, SPACE | Alpha | ✅ Updated |
| **GEO-INFER-AGENT** | [Intelligent agent frameworks for autonomous geospatial decision-making](./GEO-INFER-AGENT/README.md) | Agent configurations, spatial environments, behavior rules | Autonomous decisions, agent interactions, simulation results | ACT, AI | Alpha | ✅ Updated |
| **GEO-INFER-ANT**   | [Complex systems modeling using Active Inference principles](./GEO-INFER-ANT/README.md) | Movement data, colony parameters, environmental conditions | Emergent behaviors, optimization solutions, swarm dynamics | ACT, SIM | Alpha | ✅ Updated |
| **GEO-INFER-API**   | [API development and integration services for interoperability](./GEO-INFER-API/README.md) | Module functions, data requests, external API calls | REST/GraphQL APIs, webhooks, standardized responses | All modules | Beta | ✅ Updated |
| **GEO-INFER-APP**   | [User interfaces, accessibility tools, and application development](./GEO-INFER-APP/README.md) | Analysis results, data products, user interactions | Interactive maps, dashboards, reports, mobile apps | API, SPACE | Alpha | ✅ Updated |
| **GEO-INFER-ART**   | [Art production and aesthetics with geospatial dimensions](./GEO-INFER-ART/README.md) | Geospatial data, artistic parameters, aesthetic rules | Artistic visualizations, generative maps, aesthetic frameworks | SPACE, APP | Alpha | ✅ Updated |
| **GEO-INFER-BAYES** | [Generalized Bayesian inference processes](./GEO-INFER-BAYES/README.md) | Observations, priors, model specifications | Posterior distributions, uncertainty estimates, model evidence | MATH | Alpha | ✅ Updated |
| **GEO-INFER-BIO**   | [Bioinformatics analysis with spatial context](./GEO-INFER-BIO/README.md) | Genomic data, biological sequences, sample locations | Spatial omics analysis, phylogeographic patterns, ecological modeling | SPACE, TIME, DATA | Alpha | ✅ Updated |
| **GEO-INFER-CIV**   | [Community engagement and participatory mapping tools](./GEO-INFER-CIV/README.md) | Community input, stakeholder data, participatory mapping | STEW-MAP visualizations, community-driven spatial planning | SPACE, APP | Alpha | ✅ Updated |
| **GEO-INFER-COG**   | [Cognitive phenomena and modeling for geospatial systems](./GEO-INFER-COG/README.md) | User behavior, cognitive models, spatial perception data | Attention mechanisms, spatial memory models, trust modeling | SPACE, AI | Alpha | ✅ Updated |
| **GEO-INFER-COMMS** | [Communications within and outside of the project](./GEO-INFER-COMMS/README.md) | Project communications, documentation needs, outreach requirements | Communication strategies, documentation, public engagement | INTRA, APP | Alpha | ✅ Updated |
| **GEO-INFER-DATA**  | [Data management, ETL processes, and storage optimization](./GEO-INFER-DATA/README.md) | Raw geospatial data, external APIs, sensor feeds | Processed datasets, data pipelines, storage solutions | OPS, SEC | Alpha | ✅ Updated |
| **GEO-INFER-ECON**  | [Economic modeling with spatial dimensions](./GEO-INFER-ECON/README.md) | Economic indicators, market data, spatial boundaries | Economic models, policy analysis, market simulations | SPACE, TIME, DATA | Alpha | ✅ Updated |
| **GEO-INFER-GIT**   | [Git integration and version control workflows](./GEO-INFER-GIT/README.md) | Repository configurations, version control needs | Automated versioning, repository management, CI/CD integration | OPS | Beta | ✅ Updated |
| **GEO-INFER-HEALTH** | [Geospatial applications for public health and epidemiology](./GEO-INFER-HEALTH/README.md) | Health data, epidemiological records, environmental factors | Disease surveillance, healthcare accessibility analysis, health risk assessment | SPACE, TIME, DATA | Alpha | ✅ Updated |
| **GEO-INFER-INTRA** | [Project documentation, workflows, and ontology management](./GEO-INFER-INTRA/README.md) | Project requirements, documentation needs, ontological structures | Documentation, workflow templates, standardized ontologies | All modules | Beta | ✅ Updated |
| **GEO-INFER-IOT** | [Internet of Things sensors and spatial web integration](./GEO-INFER-IOT/README.md) | IoT sensor streams, device metadata, spatial coordinates | Real-time sensor data fusion, Bayesian spatial interpolation, global sensor networks | SPACE, BAYES, DATA | Alpha | ✅ Updated |
| **GEO-INFER-MATH**  | [Mathematical foundations and computational methods](./GEO-INFER-MATH/README.md) | Mathematical problems, spatial calculations, statistical requirements | Mathematical solutions, spatial statistics, optimization results | - | Beta | ✅ Updated |
| **GEO-INFER-NORMS** | [Social-technical compliance modeling](./GEO-INFER-NORMS/README.md) | Regulatory requirements, compliance data, social norms | Compliance tracking, regulatory impact mapping, social norm modeling | SPACE, DATA | Alpha | ✅ Updated |
| **GEO-INFER-OPS**   | [Operational kernel for system orchestration and monitoring](./GEO-INFER-OPS/README.md) | System metrics, configuration files, infrastructure requirements | Monitoring dashboards, automated deployment, system health reports | SEC | Alpha | ✅ Updated |
| **GEO-INFER-ORG**   | [Organizations and Decentralized Autonomous Organizations](./GEO-INFER-ORG/README.md) | Organizational structures, governance requirements, DAO parameters | Governance frameworks, token engineering, proposal systems | PEP, COMMS | Alpha | ✅ Updated |
| **GEO-INFER-PEP**   | [People management, HR, and CRM functions](./GEO-INFER-PEP/README.md) | Personnel data, community relationships, skill requirements | Talent management, community engagement, conflict resolution | ORG, COMMS | Alpha | ✅ Updated |
| **GEO-INFER-REQ**   | [Requirements engineering using P3IF framework](./GEO-INFER-REQ/README.md) | Requirements specifications, stakeholder needs, system constraints | Validated requirements, compliance frameworks, system specifications | NORMS, SEC | Alpha | ✅ Updated |
| **GEO-INFER-SEC**   | [Security and privacy frameworks for geospatial information](./GEO-INFER-SEC/README.md) | Security requirements, privacy constraints, access control needs | Security protocols, data anonymization, compliance frameworks | - | Alpha | ✅ Updated |
| **GEO-INFER-SIM**   | [Simulation environments for hypothesis testing](./GEO-INFER-SIM/README.md) | Model parameters, scenario definitions, simulation requirements | Digital twins, agent-based models, scenario planning tools | SPACE, TIME | Alpha | ✅ Updated |
| **GEO-INFER-SPM**   | [Statistical Parametric Mapping for spatial-temporal analysis](./GEO-INFER-SPM/README.md) | Spatial-temporal data, statistical models, field observations | GLM analysis, random field theory, cluster-level inference | MATH, SPACE | Alpha | ✅ Updated |
| **GEO-INFER-SPACE** | [Spatial methods for geospatial analysis](./GEO-INFER-SPACE/README.md) | Vector/raster data, coordinates, geometries, spatial queries | Processed spatial data, analysis results, spatial indices | DATA, MATH | Beta | ✅ **FULLY MIGRATED** |
| **GEO-INFER-TIME**  | [Temporal methods for timeline expression and dynamic data fusion](./GEO-INFER-TIME/README.md) | Time-series data, sensor streams, historical records | Forecasts, trends, temporal patterns, events | DATA, MATH | Alpha | ✅ Updated |
| **GEO-INFER-RISK**  | [Risk modeling and insurance for geospatial applications](./GEO-INFER-RISK/README.md) | Risk factors, hazard data, vulnerability assessments | Risk models, insurance pricing, exposure management | SPACE, TIME, DATA | Alpha | ✅ Updated |
| **GEO-INFER-LOG**   | [Logistics and supply chain optimization](./GEO-INFER-LOG/README.md) | Transportation networks, supply chain data, logistics requirements | Route optimization, supply chain modeling, logistics planning | SPACE, TIME, DATA | Alpha | ✅ Updated |
| **GEO-INFER-PLACE** | [Place-based analyses for specific geographic locations](./GEO-INFER-PLACE/README.md) | Location-specific data, regional datasets, local context | Regional analyses, place-based insights, territorial assessments | SPACE, TIME, DATA, ALL | Beta | ✅ **FULLY MIGRATED** |
| **GEO-INFER-TEST**  | [Testing framework for quality assurance](./GEO-INFER-TEST/README.md) | Test requirements, quality metrics, integration needs | Automated test suites, quality reports, integration validation | All modules | Alpha | ✅ Updated |
| **GEO-INFER-EXAMPLES** | [Cross-module integration demonstrations and tutorials](./GEO-INFER-EXAMPLES/README.md) | Integration requirements, tutorial needs, demonstration scenarios | Integration examples, best practices, entry-point tutorials | All modules | Beta | ✅ Updated |

## 🔄 Framework Position in Geospatial Ecosystem

```mermaid
graph TD
    %% Note: no explicit styling; keep dark-mode compatible

    GEOINFER["GEO-INFER Framework"]
    
    %% Data Sources
    RS["Remote Sensing"]
    IOT["IoT Sensors"]
    CSV["Tabular Data"]
    OSM["OpenStreetMap"]
    CGD["Crowdsourced Geodata"]
    API["External APIs"]
    SENSOR["Environmental Sensors"]
    
    %% Applications
    DT["Digital Twins"]
    CSD["Climate-Smart Decisions"]
    ES["Ecological Simulations"]
    CP["Civic Planning"]
    RM["Risk Management"]
    PA["Precision Agriculture"]
    UH["Urban Health"]
    
    %% Domains
    URB["Urban Systems"]
    ECO["Ecosystems"]
    AGR["Agriculture"]
    HLT["Health Systems"]
    FIN["Financial Systems"]
    LOG["Logistics Networks"]
    GOV["Governance Systems"]
    
    %% Integration Points
    AI_INT["AI/ML Integration"]
    ACT_INT["Active Inference"]
    H3_INT["H3 v4 Spatial Indexing"]
    
    %% Connections
    RS --> GEOINFER
    IOT --> GEOINFER
    CSV --> GEOINFER
    OSM --> GEOINFER
    CGD --> GEOINFER
    API --> GEOINFER
    SENSOR --> GEOINFER
    
    GEOINFER --> AI_INT
    GEOINFER --> ACT_INT
    GEOINFER --> H3_INT
    
    GEOINFER --> DT
    GEOINFER --> CSD
    GEOINFER --> ES
    GEOINFER --> CP
    GEOINFER --> RM
    GEOINFER --> PA
    GEOINFER --> UH
    
    DT --> URB
    CSD --> ECO
    ES --> ECO
    CP --> URB
    RM --> HLT
    PA --> AGR
    UH --> HLT
    
    AI_INT --> DT
    AI_INT --> CSD
    AI_INT --> ES
    AI_INT --> PA
    AI_INT --> UH
    
    ACT_INT --> RM
    ACT_INT --> CP
    ACT_INT --> GOV
    
    H3_INT --> LOG
    H3_INT --> FIN
```

## 🎯 Use Cases & Real-World Applications

### Environmental Management

Implement sophisticated environmental monitoring and adaptive management using SPACE, TIME, and ACT modules integrated with domain-specific modules (AG, HEALTH, RISK, BIO).

### Governance & Organizational Systems

Design and coordinate multi-level governance systems using **METAGOV** with stakeholder platforms, institutional design, and accountability mechanisms. Integrate with organizational (ORG), normative (NORMS), and security (SEC) frameworks.

### Urban & Civic Systems

Build smart city applications combining real-time spatial analysis (SPACE, IOT), cognitive modeling (COG), autonomous agents (AGENT), and community engagement (CIV, COMMS).

### Supply Chain & Logistics

Optimize complex logistics networks using spatial optimization (SPACE), temporal analysis (TIME), and economic modeling (ECON).

## Testing & Quality Assurance

### Comprehensive Testing Framework

```bash
# Run unified test suite
uv run python GEO-INFER-TEST/run_unified_tests.py

# Run specific test categories
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
uv run python GEO-INFER-TEST/run_unified_tests.py --category performance

# Run tests for specific module
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE

# Run H3 v4 migration tests
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration

# Run with pytest directly
uv run python -m pytest GEO-INFER-TEST/tests/ -v
```

## Documentation

### API Documentation

- **Core API**: [SPACE Module API](./GEO-INFER-SPACE/docs/api_schema.yaml)
- **H3 Utilities**: [H3 v4 Functions](./GEO-INFER-SPACE/src/geo_infer_space/utils/h3_utils.py)
- **Place Analysis**: [PLACE Module](./GEO-INFER-PLACE/README.md)
- **Module Docs Index**: [INTRA Modules Overview](./GEO-INFER-INTRA/docs/modules/index.md)

### Tutorials & Examples

- **Getting Started**: [Getting Started Examples](./GEO-INFER-EXAMPLES/examples/getting_started/)
- **H3 Migration**: [H3 v4 Migration Guide](./GEO-INFER-SPACE/docs/H3_V4_MIGRATION_GUIDE.md)
- **Advanced Usage**: [Module Orchestrators](./GEO-INFER-EXAMPLES/examples/module_orchestrators/)

## 👥 Contributing

We welcome contributions from developers, researchers, and geospatial professionals! GEO-INFER follows comprehensive development standards to ensure code quality and documentation excellence.

### 🚀 Quick Start for Contributors

```bash
# 1. Fork and clone
git clone https://github.com/your-username/geo-infer.git
cd GEO-INFER

# 2. Set up development environment
uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE  # Install core modules

# 3. Run tests to verify setup
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit

# 4. Check documentation standards
uv run python -c "import yaml; print('YAML validation ready')"
```

### 📋 Development Workflow

#### 1. **Choose Your Contribution Type**

- **🐛 Bug Fixes**: Fix issues in existing modules
- **✨ New Features**: Add capabilities to existing modules
- **📚 Documentation**: Improve docs, examples, or tutorials
- **🧪 Testing**: Add tests or improve test coverage
- **🔧 Infrastructure**: CI/CD, tooling, or build improvements

#### 2. **Follow Development Standards**

- **Code Quality**: Professional, functional, intelligent, modular code
- **Documentation**: Update docs simultaneously with code changes
- **Testing**: Write comprehensive tests for all functionality
- **Integration**: Ensure cross-module compatibility

#### 3. **Documentation Requirements**

- **YAML Front Matter**: Required for all new documentation
- **Working Examples**: Provide runnable code samples
- **Integration Guides**: Document cross-module interactions
- **Troubleshooting**: Include common issues and solutions

### 🎯 Key Contribution Areas

| Area | Impact | Getting Started |
|------|--------|-----------------|
| **📚 Documentation Standards** | High | Review `GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md` |
| **🔧 Core Module Development** | High | Start with MATH or SPACE modules |
| **🧪 Testing Framework** | High | Run `GEO-INFER-TEST/run_unified_tests.py` |
| **🌐 API Integration** | Medium | Work with API and APP modules |
| **📊 Domain Applications** | Medium | Contribute to AG, HEALTH, or LOG modules |
| **🎨 Visualization** | Medium | Enhance ART and APP modules |

### 🔧 Development Configuration

Each GEO-INFER module includes a module-specific `.cursorrules` file that extends the root framework rules with module-specific development guidelines, dependencies, data sources, and integration patterns. These files help ensure consistent development practices across all modules.

- **Root Rules**: `/.cursorrules` - Framework-wide development principles
- **Module Rules**: `GEO-INFER-{MODULE}/.cursorrules` - Module-specific guidelines

### 📖 Documentation Standards

#### For Code Contributions

- **Docstrings**: Comprehensive docstrings with examples
- **Type Hints**: Full type annotations for all parameters
- **Mathematical Documentation**: Document theoretical foundations
- **Integration Examples**: Show cross-module usage

#### For Documentation Contributions

- **YAML Front Matter**: Required metadata structure
- **Standard Sections**: Overview, Core Features, API Reference, Use Cases
- **Working Examples**: Tested, runnable code samples
- **Cross-Linking**: Reference related modules and docs

### 🔧 Technical Requirements

#### Code Standards

- **Python**: 3.11+ with type hints
- **Style**: PEP 8 with Black formatting
- **Testing**: Comprehensive unit and integration tests
- **Performance**: Optimize for large-scale geospatial data

#### Documentation Standards

- **Format**: Markdown with YAML front matter
- **Examples**: Working, tested code samples
- **Accessibility**: Clear, professional language
- **Maintenance**: Keep docs current with code changes

### 🚨 Important Guidelines

#### ✅ Always Do These

- Follow the established module structure
- Write comprehensive tests and documentation
- Update documentation when modifying code
- Use proper error handling (no `pass` or `NotImplementedError`)
- Implement real functionality (no mock methods)

#### ❌ Never Do These

- Create mock or placeholder implementations
- Hardcode configuration values
- Ignore error conditions
- Add unnecessary comments or redundant adjectives
- Break established API patterns

### 🏆 Recognition & Support

#### Getting Help

- **📖 Documentation**: Check `GEO-INFER-INTRA/docs/` for comprehensive guides
- **💬 Community**: Join our [Discord](https://discord.activeinference.institute/) community
- **🐛 Issues**: Report bugs or request features on GitHub
- **📧 Support**: Contact maintainers for technical guidance

#### Recognition

- **Contributors**: Listed in module READMEs and project acknowledgments
- **Documentation**: Featured in integration guides and tutorials
- **Testing**: Recognized in test coverage reports and quality metrics
- **Innovation**: Highlighted in release notes and case studies

### 🎯 Next Steps

1. **Review Standards**: Read `GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md`
2. **Choose Module**: Start with well-established modules (MATH, SPACE, ACT)
3. **Set Up Environment**: Follow the quick start guide above
4. **Make Contribution**: Implement, test, and document your changes
5. **Submit PR**: Follow our pull request template and guidelines

**Ready to contribute?** Start with our [documentation standards](GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md) and join our community of geospatial innovators!

## Community

### Join the Community

- **Discord**: [Active Inference Institute](https://discord.activeinference.institute/)
- **GitHub Discussions**: [Framework Discussions](https://github.com/geo-infer/geo-infer/discussions)
- **Documentation**: [Comprehensive Docs](./GEO-INFER-INTRA/docs/)

### Community Guidelines

- **Be Respectful**: Foster an inclusive and welcoming environment
- **Share Knowledge**: Help others learn and grow
- **Report Issues**: Contribute to framework improvement
- **Follow Standards**: Maintain code quality and documentation

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **H3 Development Team**: For the excellent H3 v4 spatial indexing library
- **Active Inference Institute**: For foundational Active Inference principles
- **Open Source Community**: For the geospatial tools and libraries that make this possible
- **Contributors**: All those who have contributed to the framework's development

---

## 🎉 Framework Status Summary

### ✅ **Completed Achievements (2026-02-25)**

| Component | Status | Details |
|-----------|--------|---------|
| **H3 v4 Migration** | ✅ **COMPLETE** | SPACE and PLACE modules fully migrated |
| **Documentation Standards** | ✅ **ESTABLISHED** | Comprehensive standards and templates created |
| **Integration Guides** | ✅ **PUBLISHED** | Cross-module tutorials and patterns documented |
| **Module Templates** | ✅ **APPLIED** | YAML front matter applied to all 44 modules (100%) |
| **Testing Framework** | ✅ **OPERATIONAL** | 434 test files, ~3,000+ tests across all 44 modules |
| **Code Quality** | ✅ **PROFESSIONAL** | 860 source files, 297,360 lines of real implementations |
| **Infrastructure** | ✅ **COMPLETE** | All modules have requirements.txt and pyproject.toml; all package dirs use PEP 8 lowercase naming |
| **Examples** | ✅ **COMPLETE** | Working examples added to all modules |
| **Integration Tests** | ✅ **COMPLETE** | Cross-module integration test suites |
| **Stub Elimination** | ✅ **COMPLETE** | Zero illegitimate pass stubs (only abstract methods/exception handlers) |
| **PEP 8 Compliance** | ✅ **COMPLETE** | All 44 modules use lowercase `geo_infer_<module>` package dirs |

### 📊 **Current Compliance Status**

#### **Documentation Compliance**

- ✅ **YAML Front Matter**: 100% (44/44 modules)
- ✅ **API Reference Sections**: 100% (24/24 target modules)
- ✅ **Core Features Sections**: 100% (standardized across all modules)
- ⚠️ **Use Cases Sections**: ~80% (needs expansion in some modules)

#### **Infrastructure Compliance**

- ✅ **requirements.txt**: 100% (44/44 modules)
- ✅ **setup.py/pyproject.toml**: 100% (44/44 modules)
- ✅ **Package Structure**: 100% (all modules follow standard structure)
- ✅ **Examples Directory**: 100% (all modules have working examples)

#### **Testing Compliance**

- ✅ **Test Suites**: 100% (44/44 modules have tests, minimum 4 test files each)
- ✅ **Test Coverage**: 434 test files, ~3,000+ tests
- ✅ **Integration Tests**: Cross-module test suites covering:
  - SPACE + TIME + DATA workflows
  - ACT + AGENT + ANT coordination
  - AI + SPACE + domain modules (AG, HEALTH, ECON)
  - SEC + API + APP security flows
- ✅ **Unified Test Runner**: Operational with test discovery and coverage reporting

#### **Module Status Breakdown**

- ✅ **Beta (Production Ready)**: 20 modules (MATH, ACT, BAYES, SPACE, IOT, API, AG, HEALTH, BIO, CLIMATE, FOREST, COMMS, APP, ART, PLACE, INTRA, GIT, TEST, EXAMPLES, LOG)
- 🟡 **Alpha (In Development)**: 24 modules (AI, COG, AGENT, SPM, TIME, DATA, SEC, OPS, METAGOV, ECON, RISK, ENERGY, WATER, TRANSPORT, MARINE, EMERGENCY, EDU, SIM, ANT, CIV, PEP, ORG, NORMS, REQ)

### 🚀 **Recent Improvements**

#### **Phase 7: Comprehensive 44-Module Improvement (2026-02-25)** ✅ Complete

10 parallel agent groups systematically improved all 44 modules:

**Foundation Modules (MATH, SPACE, TIME, DATA)**:

- Fixed 3 MATH convenience API stubs, implemented ALS CP decomposition, fixed optimizer bug
- Verified H3 v4 API consistency across SPACE (zero legacy v3 calls)
- Added 340+ tests to TIME, 177+ tests to DATA, fixed interpolation bugs

**Core Analytics (BAYES, ACT, SPM, AI, COG)**:

- BAYES: Implemented real Gaussian Process (Cholesky-based, RBF/Matern/Exponential kernels), replaced random-number model comparison with LOO/WAIC/DIC/AIC/BIC
- ACT: Fixed 8 stubs including numpy array truth-value bug in free_energy.py, implemented perception-action loop closure
- AI: Fixed missing Tuple import that blocked all tests, added 79 tests
- COG: Fixed 5 broken f-strings, 2 validation bugs, added 146 tests

**Agent Architecture (AGENT, ANT, SIM)**:

- AGENT: 10 new test files (140 tests), compatibility fixes
- ANT: Verified swarm algorithms, added integration tests
- SIM: Expanded simulation types, added tests

**Environmental Domains (FOREST, MARINE, ENERGY, WATER, CLIMATE)**:

- All package dirs now use PEP 8 lowercase naming (`geo_infer_forest`, `geo_infer_marine`, `geo_infer_energy`, `geo_infer_water`).
- Added 14 new source files with real domain algorithms, 286 tests, fixed 8 bugs

**Applied Domains (HEALTH, ECON, RISK, AG, BIO, EMERGENCY, TRANSPORT, EDU, LOG)**:

- 740 tests across 72 test files in 9 modules
- Fixed RISK broken EarthquakeModel, LOG ortools degradation, BIO deprecated imports
- Created real AG API resources (FieldsResource, CropsResource, YieldResource)

**Governance & Infrastructure (NORMS, METAGOV, SEC, COMMS, GIT, IOT, PEP)**:

- 522 tests across 7 modules
- Fixed circular imports (COMMS), datetime comparison (SEC), missing typing imports (IOT)

**Application Layer (CIV, ORG, REQ, API, APP, OPS, EXAMPLES, INTRA, ART, PLACE)**:

- CIV/ORG/REQ: Implemented from scratch — participation platform (Shannon entropy), organization model (directed graph + 6 voting methods), requirements analyzer (topological sort + critical path)
- 527 tests across 10 modules

#### **Phase 1-6: Infrastructure, Documentation & Testing (2025-01-19)** ✅ Complete

- Added `requirements.txt` to 25 modules, `setup.py` to 13 modules
- Created test suites, API Reference sections, YAML front matter (100%)
- Enhanced AI, TIME, SIM, ANT modules with real algorithms
- Created 4 cross-module integration test suites
- Added working examples to all modules

### 🎯 **Current Development Focus**

#### **High Priority (Immediate)**

- ✅ Complete YAML template application → **DONE**
- ✅ Develop comprehensive cross-module integration tests → **DONE**
- ✅ Add working examples to all modules → **DONE**
- ✅ Expand test coverage for all modules (416 test files) → **DONE**
- ✅ Eliminate all illegitimate stubs → **DONE**
- ✅ Fix PEP 8 package naming violations → **DONE**
- ⏳ Implement performance benchmarks and optimization guidelines
- ⏳ Establish CI/CD pipelines

#### **Medium Priority (Next Phase)**

- ⏳ Expand Use Cases sections with practical examples
- ⏳ Create domain-specific integration tutorials
- ⏳ Implement automated documentation generation
- ⏳ Upgrade remaining 16 Alpha modules to Beta

### 📞 **Get Involved**

**🌟 New to GEO-INFER?**

- Start with our [Quick Start Guide](#-quick-start)
- Explore [Integration Examples](GEO-INFER-INTRA/docs/guides/)
- Join our [Discord Community](https://discord.activeinference.institute/)

**👨‍💻 Want to Contribute?**

- Review our [Documentation Standards](GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md)
- Check the [Module Index](GEO-INFER-INTRA/docs/modules/index.md)
- Run the [Unified Test Suite](GEO-INFER-TEST/run_unified_tests.py)

**🔬 Research & Development?**

- Explore [Active Inference Modules](GEO-INFER-ACT/)
- Work with [Spatial Analysis](GEO-INFER-SPACE/) (H3 v4 ready)
- Contribute to [Domain Applications](./GEO-INFER-AG/) or [Health Module](./GEO-INFER-HEALTH/)

### 🤝 **Community & Support**

- **📚 Documentation**: Comprehensive guides in `GEO-INFER-INTRA/docs/`
- **💬 Community**: Active discussion on [Discord](https://discord.activeinference.institute/)
- **🐛 Issues**: Report bugs and request features on GitHub
- **📧 Support**: Technical guidance from maintainers
- **🎓 Learning**: Tutorials, examples, and integration guides

---

**🌍 GEO-INFER Framework** | **Framework Version**: 0.2.0 | **H3 Version**: v4.0+ | **Python**: 3.11+
**📅 Last Updated**: 2026-04-16 | **📋 Documentation**: ✅ **COMPREHENSIVE** | **🧪 Testing**: ✅ **434 files, ~3,000+ tests**
**Maintained by**: GEO-INFER Community | **License**: CC BY-NC-SA 4.0 | **Methodology**: [PAI Algorithm](./PAI.md)

*Building the future of geospatial inference through Active Inference principles and collaborative development.*
