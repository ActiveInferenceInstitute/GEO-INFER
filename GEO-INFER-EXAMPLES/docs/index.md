# GEO-INFER Examples Gallery > **Historical analysis document.** This file is an assessment-era analysis > (June 2025) and may not reflect the current repository state. Treat its > metrics, API sketches, and integration claims as historical; verify against > the current module sources, `GEO-INFER-TEST/` validators, and the INTRA > documentation hub before relying on them.
> Working code examples demonstrating GEO-INFER capabilities across all domains.
This gallery covers every example shipped in the `GEO-INFER-EXAMPLES` module, organized by difficulty, domain, and module dependency. Each entry links to its source directory and lists the GEO-INFER modules required to run it.
---
## Quick Navigation
| Section | Description |
|---------|-------------|
| [How to Run Examples](#how-to-run-examples) | Setup and execution instructions |
| [Beginner Examples](#beginner-30-minutes) | Getting started, basic integration |
| [Intermediate Examples](#intermediate-30-90-minutes) | Domain integrations, multi-module workflows |
| [Advanced Examples](#advanced-90-minutes) | Full pipelines, orchestrators, dashboards |
| [Module Orchestrators](#module-orchestrators) | Per-module orchestrator scripts for all 45 modules |
| [Examples by Module](#examples-by-module) | Cross-reference table of modules to examples |
| [Contributing Examples](#contributing-examples) | How to add a new example |
---
## How to Run Examples
### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- GEO-INFER repository cloned locally
### General Pattern
```bash
# 1. Install the modules required by the example
uv pip install -e ./GEO-INFER-SPACE ./GEO-INFER-DATA ./GEO-INFER-MATH
# 2. Navigate to the examples module
cd GEO-INFER-EXAMPLES
# 3. Run a specific example script
uv run python examples/<category>/<example_name>/scripts/run_example.py
```
### Quick Verification ```
```bash
# Run the basic integration demo to verify your setup
uv pip install -e ./GEO-INFER-EXAMPLES
uv run python GEO-INFER-EXAMPLES/examples/getting_started/basic_integration_demo/scripts/run_example.py
```
---
## Examples by Difficulty
### Beginner (< 30 minutes)
Examples suitable for first-time users who want to understand how GEO-INFER modules connect.
#### 1. Basic Integration Demo
- **Path**: `examples/getting_started/basic_integration_demo/`
- **Entry point**: `scripts/run_example.py`
- **Modules used**: SPACE, DATA, MATH
- **Description**: Demonstrates the fundamental pattern of loading spatial data, performing a simple analysis with MATH, and visualizing results through SPACE. The minimal starting point for all GEO-INFER work.
- **What you will learn**:
- How modules import and interact
- Basic spatial data structures
- Running an analysis pipeline end-to-end ```
```bash
uv pip install -e ./GEO-INFER-SPACE ./GEO-INFER-DATA ./GEO-INFER-MATH
uv run python GEO-INFER-EXAMPLES/examples/getting_started/basic_integration_demo/scripts/run_example.py
```
---
### Intermediate (30-90 minutes)
Multi-module examples that integrate domain-specific analysis with spatial infrastructure.
#### 2. Agriculture Integration: Precision Farming System
- **Path**: `examples/agriculture_integration/precision_farming_system/`
- **Entry point**: `scripts/run_example.py`
- **Modules used**: AG, SPACE, DATA, IOT, TIME
- **Description**: Implements a precision farming workflow that combines IoT sensor data (soil moisture, temperature) with spatial analysis on H3 grids and temporal trend detection. Demonstrates real-time agricultural decision support.
- **What you will learn**:
- IoT data ingestion and spatial indexing
- Agricultural domain analysis patterns
- Time-series integration with spatial grids ```
```bash
uv pip install -e ./GEO-INFER-AG ./GEO-INFER-SPACE ./GEO-INFER-DATA \
./GEO-INFER-IOT ./GEO-INFER-TIME
uv run python GEO-INFER-EXAMPLES/examples/agriculture_integration/precision_farming_system/scripts/run_example.py
```
#### 3. Health Integration: Disease Surveillance Pipeline
- **Path**: `examples/health_integration/disease_surveillance_pipeline/`
- **Entry point**: `scripts/run_surveillance_pipeline.py`
- **Modules used**: HEALTH, SPACE, DATA, BAYES, TIME
- **Description**: Builds a spatial disease surveillance system that uses Bayesian inference to identify outbreak clusters and temporal analysis to detect emerging trends. Covers the full pipeline from raw health records to spatial risk maps.
- **What you will learn**:
- Health data spatial aggregation
- Bayesian cluster detection
- Temporal outbreak pattern recognition ```
```bash
uv pip install -e ./GEO-INFER-HEALTH ./GEO-INFER-SPACE ./GEO-INFER-DATA \
./GEO-INFER-BAYES ./GEO-INFER-TIME
uv run python GEO-INFER-EXAMPLES/examples/health_integration/disease_surveillance_pipeline/scripts/run_surveillance_pipeline.py
```
#### 4. IoT Radiation Monitoring
- **Path**: `examples/iot_radiation_monitoring/`
- **Entry point**: `scripts/run_example.py`
- **Modules used**: IOT, SPACE, DATA, RISK
- **Description**: Processes radiation sensor network data, performs spatial interpolation to create continuous exposure maps, and applies risk assessment models. Includes visualization scripts for producing publication-ready maps.
- **Additional scripts**:
- `scripts/enhanced_visualization.py` -- generates styled map outputs
- **What you will learn**:
- Sensor network data processing
- Spatial interpolation techniques
- Risk model integration ```
```bash
uv pip install -e ./GEO-INFER-IOT ./GEO-INFER-SPACE ./GEO-INFER-DATA \
./GEO-INFER-RISK
uv run python GEO-INFER-EXAMPLES/examples/iot_radiation_monitoring/scripts/run_example.py
```
#### 5. Climate Integration: Spatial Microbiome-Soil-Climate
- **Path**: `examples/climate_integration/spatial_microbiome_soil_climate/`
- **Entry point**: `scripts/run_example.py`
- **Modules used**: CLIMATE, BIO, SPACE, DATA, BAYES
- **Description**: Integrates soil microbiome data with climate variables and spatial analysis to study how microbial communities respond to environmental gradients. Uses Bayesian models for uncertainty quantification.
- **Additional scripts**:
- `scripts/run_spatial_integration.py` -- runs the spatial join and analysis steps
- **Documentation**:
- `SPECIFICATION.md` -- detailed data layer specifications
- `USAGE_GUIDE.md` -- step-by-step usage instructions
- `DATA_LAYERS_VERIFIED.md` -- verification of input data layers
- **What you will learn**:
- Multi-domain data fusion (climate + biology + soil)
- Bayesian uncertainty quantification
- Environmental gradient analysis ```
```bash
uv pip install -e ./GEO-INFER-CLIMATE ./GEO-INFER-BIO ./GEO-INFER-SPACE \
./GEO-INFER-DATA ./GEO-INFER-BAYES
uv run python GEO-INFER-EXAMPLES/examples/climate_integration/spatial_microbiome_soil_climate/scripts/run_example.py
```
---
### Advanced (90+ minutes)
Full-scale examples involving interactive dashboards, complex multi-module pipelines, and orchestration patterns.
#### 6. Area Study Template
- **Path**: `examples/area_study/`
- **Entry point**: `scripts/run_example.py`
- **Modules used**: SPACE, DATA, PLACE, PEP, IOT, BIO, HEALTH, TIME, AG, ECON, RISK, API, APP, NORMS
- **Description**: A multi-disciplinary area analysis framework that combines technical infrastructure monitoring, social systems analysis, and environmental assessment into a unified research and planning tool. Produces an interactive Streamlit dashboard with togglable map layers.
- **Additional scripts**:
- `scripts/launch_dashboard.py` -- starts the Streamlit dashboard
- `scripts/dashboard_app.py` -- the Streamlit application
- `scripts/simple_launch.py` -- minimal launcher
- `scripts/show_results.py` -- display pre-computed results
- **Documentation**:
- `docs/methodology_guide.md` -- research methodology
- `docs/validation_framework.md` -- data validation approach
- **What you will learn**:
- Integrating 10+ modules in a single pipeline
- Building interactive dashboards with spatial overlays
- Multi-scale H3 analysis (resolution 7-11)
- Community-engaged data collection patterns ```
```bash
uv pip install -e ./GEO-INFER-SPACE ./GEO-INFER-DATA ./GEO-INFER-PLACE \
./GEO-INFER-PEP ./GEO-INFER-IOT ./GEO-INFER-BIO ./GEO-INFER-HEALTH \
./GEO-INFER-TIME ./GEO-INFER-ECON ./GEO-INFER-RISK ./GEO-INFER-API \
./GEO-INFER-APP ./GEO-INFER-NORMS
uv run python GEO-INFER-EXAMPLES/examples/area_study/scripts/run_example.py
```
---
## Module Orchestrators
Each of the 45 GEO-INFER modules has a dedicated orchestrator example under `examples/module_orchestrators/<MODULE>/`. These demonstrate the standalone capabilities of each module through a standardized script interface.
### Running an Orchestrator ```
```bash
# General pattern
uv pip install -e ./GEO-INFER-<MODULE>
uv run python GEO-INFER-EXAMPLES/examples/module_orchestrators/<MODULE>/scripts/run_orchestrator.py
```
### Available Orchestrators
| Module | Path | Primary Domain |
|--------|------|----------------|
| ACT | `module_orchestrators/ACT/` | Active Inference |
| AG | `module_orchestrators/AG/` | Agriculture |
| AGENT | `module_orchestrators/AGENT/` | Agent Systems |
| AI | `module_orchestrators/AI/` | Machine Learning |
| ANT | `module_orchestrators/ANT/` | Ant Colony Optimization |
| API | `module_orchestrators/API/` | API Gateway |
| APP | `module_orchestrators/APP/` | Application Framework |
| ART | `module_orchestrators/ART/` | Creative/Generative |
| BAYES | `module_orchestrators/BAYES/` | Bayesian Inference |
| BIO | `module_orchestrators/BIO/` | Biodiversity |
| CIV | `module_orchestrators/CIV/` | Civic Engagement |
| COG | `module_orchestrators/COG/` | Cognitive Science |
| COMMS | `module_orchestrators/COMMS/` | Communications |
| DATA | `module_orchestrators/DATA/` | Data Integration |
| ECON | `module_orchestrators/ECON/` | Economics |
| GIT | `module_orchestrators/GIT/` | Version Control |
| HEALTH | `module_orchestrators/HEALTH/` | Health Analytics |
| INSURANCE | `module_orchestrators/INSURANCE/` | Insurance Operations |
| INTRA | `module_orchestrators/INTRA/` | Internal Documentation |
| IOT | `module_orchestrators/IOT/` | IoT Sensors |
| LOG | `module_orchestrators/LOG/` | Logistics |
| MATH | `module_orchestrators/MATH/` | Mathematics |
| NORMS | `module_orchestrators/NORMS/` | Normative Compliance |
| OPS | `module_orchestrators/OPS/` | Operations |
| ORG | `module_orchestrators/ORG/` | Organizations |
| PEP | `module_orchestrators/PEP/` | People Analytics |
| PLACE | `module_orchestrators/PLACE/` | Place Intelligence |
| REQ | `module_orchestrators/REQ/` | Requirements |
| RISK | `module_orchestrators/RISK/` | Risk Assessment |
| SEC | `module_orchestrators/SEC/` | Security |
| SIM | `module_orchestrators/SIM/` | Simulation |
| SPACE | `module_orchestrators/SPACE/` | Spatial Analysis |
| SPM | `module_orchestrators/SPM/` | Spatial Process Models |
| TEST | `module_orchestrators/TEST/` | Testing Framework |
| TIME | `module_orchestrators/TIME/` | Temporal Analysis |
Note: Modules not listed (CLIMATE, EDU, EMERGENCY, ENERGY, FOREST, MARINE, TRANSPORT, WATER) do not yet have dedicated orchestrator examples. Contributions are welcome.
---
## Examples by Module
Cross-reference of which examples use each module.
| Module | Examples |
|--------|----------|
| SPACE | Basic Integration Demo, Agriculture Integration, Health Surveillance, IoT Radiation, Climate Microbiome, Area Study |
| DATA | Basic Integration Demo, Agriculture Integration, Health Surveillance, IoT Radiation, Climate Microbiome, Area Study |
| MATH | Basic Integration Demo |
| AG | Agriculture Integration |
| IOT | Agriculture Integration, IoT Radiation, Area Study |
| TIME | Agriculture Integration, Health Surveillance, Area Study |
| HEALTH | Health Surveillance, Area Study |
| BAYES | Health Surveillance, Climate Microbiome |
| RISK | IoT Radiation, Area Study |
| CLIMATE | Climate Microbiome |
| INSURANCE | Insurance Operations Orchestrator (`examples/module_orchestrators/INSURANCE/`) |
| BIO | Climate Microbiome, Area Study |
| PLACE | Area Study |
| PEP | Area Study |
| ECON | Area Study |
| API | Area Study |
| APP | Area Study |
| NORMS | Area Study |
---
## Core Library Components
Beyond the runnable examples, the `GEO-INFER-EXAMPLES` module includes library code under `src/geo_infer_examples/`:
| Component | Path | Description |
|-----------|------|-------------|
| Module Orchestrator | `core/module_orchestrator.py` | Base class for coordinating multi-module workflows |
| Integration Models | `models/integration_models.py` | Data models shared across example pipelines |
These are imported by the example scripts and can be reused when building custom pipelines.
---
## Contributing Examples
### Required Structure
Every new example must follow this layout:
```
examples/<category>/<example_name>/
README.md # Description, modules used, learning objectives
scripts/
run_example.py # Main entry point (standardized name)
config/ # Optional: YAML/JSON configuration files
docs/ # Optional: detailed documentation
output/ # Optional: gitignored output directory
```
### Standards for Examples
1. **Self-contained**: Each example must list all required modules in its README.
2. **Runnable**: The `scripts/run_example.py` entry point must work after installing the listed dependencies.
3. **Documented**: Include a README with learning objectives, prerequisites, and expected output.
4. **Tested**: Add at least one test under `GEO-INFER-EXAMPLES/tests/` to verify the example runs without errors.
5. **No hardcoded paths**: Use relative paths and environment variables for any data locations.
6. **Graceful degradation**: If optional modules are not installed, print a clear message rather than crashing.
### Adding a New Example ```
```bash
# 1. Create the directory structure
mkdir -p GEO-INFER-EXAMPLES/examples/<category>/<example_name>/scripts
mkdir -p GEO-INFER-EXAMPLES/examples/<category>/<example_name>/config
# 2. Create the entry point
touch GEO-INFER-EXAMPLES/examples/<category>/<example_name>/scripts/run_example.py
# 3. Create the README
touch GEO-INFER-EXAMPLES/examples/<category>/<example_name>/README.md
# 4. Add a test
touch GEO-INFER-EXAMPLES/tests/unit/test_<example_name>.py
# 5. Run the example to verify
uv run python GEO-INFER-EXAMPLES/examples/<category>/<example_name>/scripts/run_example.py
```
---
## Related Documentation
- [GEO-INFER-TEST README](../../GEO-INFER-TEST/README.md) -- Testing infrastructure and runner flags
- [Integration Guide](./INTEGRATION_GUIDE.md) -- Cross-module integration patterns
- [Technical Architecture Guide](./TECHNICAL_ARCHITECTURE_GUIDE.md) -- System architecture overview
- [Performance Benchmarking Guide](./PERFORMANCE_BENCHMARKING_GUIDE.md) -- Benchmarking methodology
- [API Integration Guide](./API_INTEGRATION_GUIDE.md) -- API endpoint patterns
- [Cross-Module Reference](./CROSS_MODULE_REFERENCE.md) -- Module dependency map
