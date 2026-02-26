# GEO-INFER Framework Overview

## What Is GEO-INFER

GEO-INFER is a 44-module Python framework for geospatial inference built on
Active Inference principles. It treats geographic systems --- ecosystems, cities,
watersheds, agricultural fields, transportation networks --- as adaptive systems
that maintain beliefs about their environment, update those beliefs from
observations, and select actions to minimize expected surprise.

The framework provides a unified mathematical foundation for spatial analysis,
temporal modeling, probabilistic inference, and decision-making under uncertainty.
It is implemented as a Python monorepo using `uv` as the package manager, with
Python 3.9+ required.

### Current Scale

- 44 modules
- 901 source files (307,361 lines of code)
- 466 test files (89,179 lines of test code)
- 3,000+ tests

## Why Active Inference for Geospatial

Traditional geospatial analysis operates on static datasets: load data, apply
algorithm, produce output. This works for descriptive analysis but breaks down
when systems need to:

- **Adapt to new information**: update predictions as new satellite imagery,
  sensor data, or survey results arrive
- **Quantify uncertainty**: distinguish between "we know X is true" and "we
  believe X with 70% confidence"
- **Make decisions**: select monitoring locations, prioritize conservation areas,
  or route emergency vehicles
- **Balance exploration and exploitation**: decide whether to gather more
  information or act on current beliefs

Active Inference provides a single mathematical framework that handles all four.
A geospatial system modeled as an Active Inference agent:

1. Maintains a **generative model** of the spatial process
2. Performs **perceptual inference** to update beliefs from observations
3. Selects **policies** (actions) that minimize expected free energy
4. Naturally balances information-seeking and goal-directed behavior

This maps directly to real geospatial workflows: monitoring programs update
beliefs about ecosystem health; urban planners evaluate interventions against
models of traffic and land use; climate scientists assimilate observations into
forecast models.

## Module Organization

### Analytical Core (7 modules)

The mathematical and computational foundation for the framework.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-MATH** | `geo_infer_math` | Linear algebra, spatial statistics, optimization, transforms |
| **GEO-INFER-ACT** | `geo_infer_act` | Active Inference engine: generative models, free energy, policy selection |
| **GEO-INFER-BAYES** | `geo_infer_bayes` | Bayesian inference: MCMC, variational methods, model comparison |
| **GEO-INFER-AI** | `geo_infer_ai` | Machine learning and deep learning integration |
| **GEO-INFER-COG** | `geo_infer_cog` | Cognitive modeling, attention mechanisms, perceptual hierarchies |
| **GEO-INFER-AGENT** | `geo_infer_agent` | Multi-agent Active Inference systems and coordination |
| **GEO-INFER-SPM** | `geo_infer_spm` | Statistical parametric mapping for spatial inference |

### Spatial-Temporal (3 modules)

Data structures and operations for space and time.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-SPACE** | `geo_infer_space` | Spatial indexing (H3 v4), geometry operations, visualization |
| **GEO-INFER-TIME** | `geo_infer_time` | Temporal analysis, forecasting, seasonality decomposition |
| **GEO-INFER-IOT** | `geo_infer_iot` | IoT sensor integration, streaming data, edge processing |

### Infrastructure (5 modules)

Platform services consumed by all other modules.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-DATA** | `geo_infer_data` | Data loading, storage, format conversion, caching |
| **GEO-INFER-API** | `geo_infer_api` | REST and WebSocket API interfaces |
| **GEO-INFER-SEC** | `geo_infer_sec` | Authentication, authorization, encryption |
| **GEO-INFER-OPS** | `geo_infer_ops` | Deployment, monitoring, scaling |
| **GEO-INFER-METAGOV** | `geo_infer_metagov` | Meta-governance and policy frameworks |

### Domain-Specific (14 modules)

Modules targeting specific application domains.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-AG** | `geo_infer_ag` | Agriculture: crop monitoring, yield prediction, soil analysis |
| **GEO-INFER-HEALTH** | `geo_infer_health` | Health: epidemiology, disease surveillance, health access |
| **GEO-INFER-ECON** | `geo_infer_econ` | Economics: market analysis, bioregional economics |
| **GEO-INFER-RISK** | `geo_infer_risk` | Risk: hazard modeling, vulnerability, catastrophe models |
| **GEO-INFER-LOG** | `geo_infer_log` | Logistics: supply chain, delivery routing, warehouse planning |
| **GEO-INFER-BIO** | `geo_infer_bio` | Ecology: biodiversity, species distribution, habitat analysis |
| **GEO-INFER-CLIMATE** | `geo_infer_climate` | Climate: anomaly detection, trend extraction, downscaling |
| **GEO-INFER-ENERGY** | `geo_infer_energy` | Energy: renewable siting, grid analysis, demand modeling |
| **GEO-INFER-FOREST** | `geo_infer_forest` | Forestry: canopy analysis, fire risk, carbon stock |
| **GEO-INFER-MARINE** | `geo_infer_marine` | Marine: ocean monitoring, fisheries, coastal analysis |
| **GEO-INFER-EMERGENCY** | `geo_infer_emergency` | Emergency: disaster response, evacuation, resource allocation |
| **GEO-INFER-EDU** | `geo_infer_edu` | Education: spatial learning, curriculum integration |
| **GEO-INFER-TRANSPORT** | `geo_infer_transport` | Transport: routing, traffic modeling, network analysis |
| **GEO-INFER-WATER** | `geo_infer_water` | Water: hydrology, water quality, watershed management |

### Agent and Simulation (2 modules)

Agent-based modeling and simulation environments.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-ANT** | `geo_infer_ant` | Ant colony optimization, swarm intelligence |
| **GEO-INFER-SIM** | `geo_infer_sim` | Simulation environments, scenario modeling |

Note: GEO-INFER-AGENT appears in Analytical Core as the core agent framework
and also participates in agent-based simulation workflows.

### Community and Applications (6 modules)

Human-facing modules for civic participation, communication, and applications.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-CIV** | `geo_infer_civ` | Urban planning, civic engagement, public infrastructure |
| **GEO-INFER-PEP** | `geo_infer_pep` | People, demographics, CRM |
| **GEO-INFER-ORG** | `geo_infer_org` | Organizational modeling and analysis |
| **GEO-INFER-COMMS** | `geo_infer_comms` | Communications, messaging, spatial routing |
| **GEO-INFER-APP** | `geo_infer_app` | Application layer, dashboards, UI components |
| **GEO-INFER-ART** | `geo_infer_art` | Creative and artistic geospatial applications |

### Governance (2 modules)

Standards compliance and requirements management.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-NORMS** | `geo_infer_norms` | Normative compliance, regulatory tracking |
| **GEO-INFER-REQ** | `geo_infer_req` | Requirements specification and validation |

### Operations and Tooling (5 modules)

Development infrastructure and meta-tooling.

| Module | Package | Description |
|--------|---------|-------------|
| **GEO-INFER-INTRA** | `geo_infer_intra` | Documentation hub, knowledge integration |
| **GEO-INFER-GIT** | `geo_infer_git` | Git workflow integration |
| **GEO-INFER-TEST** | `geo_infer_test` | Unified test runner, test infrastructure |
| **GEO-INFER-EXAMPLES** | `geo_infer_examples` | Example code, module orchestrator |
| **GEO-INFER-PLACE** | `geo_infer_place` | Place-based analysis, bioregional studies |

## Architecture

### Data Flow

```text
                    +------------------+
                    |   Data Sources   |
                    | Sensors, Imagery |
                    | Surveys, APIs    |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |   GEO-INFER-DATA |
                    |   Load, Store,   |
                    |   Transform      |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  SPACE  |  TIME  |
                    |  Spatial  Temporal|
                    |  Indexing Analysis|
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v-------+
     |    MATH    |  |    BAYES    |  |    ACT     |
     | Statistics |  | Probabilistic|  | Active    |
     | Transforms |  | Inference   |  | Inference |
     +--------+---+  +------+------+  +----+-------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v---------+
                    |   AI  |  AGENT  |
                    |  ML Models  Multi|
                    |  Prediction Agent|
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v-------+
     | AG, FOREST |  | RISK, ECON  |  | CIV, TRANS |
     | MARINE,BIO |  | HEALTH,LOG  |  | EMERGENCY  |
     | CLIMATE    |  | ENERGY      |  | WATER,EDU  |
     +--------+---+  +------+------+  +----+-------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v---------+
                    |   API  |  APP   |
                    |  Endpoints  UI  |
                    |  Services  Viz  |
                    +------------------+
```

### Dependency Graph

Foundation modules have zero internal dependencies. Each layer depends only on
layers below it.

```text
Layer 0 (Foundation):   MATH
Layer 1 (Core):         ACT, BAYES           [depend on MATH]
Layer 2 (Spatial):      SPACE, TIME, DATA    [depend on MATH]
Layer 3 (Intelligence): AI, AGENT, COG, SPM  [depend on Layers 0-2]
Layer 4 (Domain):       AG, HEALTH, RISK...  [depend on Layers 0-3]
Layer 5 (Interface):    API, APP             [depend on Layers 0-4]
```

Cross-cutting modules (SEC, OPS, NORMS, TEST) provide services to all layers
without introducing circular dependencies.

## Key Use Cases

### Agriculture

Monitor crop health across thousands of hectares using satellite imagery, predict
yields using Bayesian models, and optimize irrigation schedules through Active
Inference policy selection.

**Modules**: AG, SPACE, TIME, BAYES, ACT, DATA

### Climate Analysis

Detect temperature and precipitation anomalies, extract long-term trends from
climate records, and downscale global climate model output to local resolution.

**Modules**: CLIMATE, TIME, SPACE, MATH, BAYES

### Urban Planning

Model traffic patterns, evaluate infrastructure investments, simulate urban
growth scenarios, and optimize public transit routing.

**Modules**: CIV, TRANSPORT, SPACE, TIME, ACT, SIM

### Risk Assessment

Build catastrophe models for natural hazards (flood, earthquake, wildfire),
assess building vulnerability using fragility curves, and compute probable
maximum loss for insurance portfolios.

**Modules**: RISK, SPACE, BAYES, ECON

### Conservation

Prioritize conservation areas using biodiversity indices, model species
distribution under climate change, track habitat connectivity, and evaluate
the effectiveness of protected areas.

**Modules**: BIO, FOREST, MARINE, SPACE, TIME, ACT

### Transportation

Analyze road network connectivity, model traffic congestion, optimize delivery
routes, and plan emergency evacuation.

**Modules**: TRANSPORT, LOG, SPACE, TIME, EMERGENCY

## Performance Characteristics

### Typical Scale

| Scenario | Data Size | Typical Runtime |
|----------|-----------|-----------------|
| H3 grid over a city (res 9) | 10,000-100,000 cells | Seconds |
| National-scale raster analysis | 1-10 GB GeoTIFF | Minutes |
| Multi-year time series (hourly) | 50,000-500,000 rows | Seconds to minutes |
| Bayesian GP regression | 1,000-10,000 training points | Minutes to hours |
| MCMC inference (4 chains) | Varies | Minutes to hours |
| Agent-based simulation (1,000 agents, 1,000 steps) | In-memory | Minutes |

### Memory Usage

- H3 operations: ~100 bytes per cell (cell ID + attributes)
- GeoDataFrame: ~500 bytes per row (geometry + 5 float columns)
- Raster: raw array size + ~20% overhead
- Active Inference state vectors: negligible for < 100 states

### Parallelization

- numpy/scipy operations: automatic via BLAS/LAPACK
- H3 operations: per-cell operations are embarrassingly parallel
- MCMC: multi-chain parallelism via joblib or multiprocessing
- Raster: chunk-based parallelism via dask or xarray

## GEO-INFER vs Alternatives

| Feature | GEO-INFER | GeoPandas Alone | PostGIS | Google Earth Engine |
|---------|-----------|----------------|---------|---------------------|
| Active Inference | Native | None | None | None |
| Bayesian inference | GEO-INFER-BAYES | Manual | None | Limited |
| H3 spatial indexing | Native (v4) | Manual install | Extension | Limited |
| Time series analysis | GEO-INFER-TIME | Manual | Limited | Native |
| Multi-agent systems | GEO-INFER-AGENT | None | None | None |
| Domain modules | 14 domains | None | None | None |
| Uncertainty quantification | Native | Manual | None | Limited |
| Local execution | Yes | Yes | Yes | No (cloud only) |
| Python-native | Yes | Yes | No (SQL) | No (JavaScript/Python API) |
| Open source | Yes | Yes | Yes | No |

GEO-INFER is the appropriate choice when you need:
- Probabilistic inference combined with spatial analysis
- Active Inference for decision-making under spatial uncertainty
- A modular Python framework you can extend with custom domain logic
- Local execution with full control over data and computation

GeoPandas alone is sufficient when you need only vector geometry operations
without probabilistic modeling. PostGIS is preferable for SQL-based spatial
queries in production databases. Google Earth Engine is suited for large-scale
remote sensing analysis on Google's infrastructure.

## Quick Start Code Example

This example demonstrates the core GEO-INFER workflow: load spatial data, index
with H3, compute statistics, and run Active Inference belief updating.

```python
import numpy as np
import h3
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator

# Step 1: Create an H3 grid over a study area
center_lat, center_lng = 45.5231, -122.6765
center_cell = h3.latlng_to_cell(center_lat, center_lng, 9)
study_area = h3.grid_disk(center_cell, 3)
print(f"Study area: {len(study_area)} H3 cells at resolution 9")

# Step 2: Define an Active Inference generative model
# 3 hidden states: healthy, stressed, degraded
# 3 observation types: high_NDVI, medium_NDVI, low_NDVI
model = GenerativeModel(model_type="categorical")

A = np.array([
    [0.8, 0.2, 0.05],  # high NDVI
    [0.15, 0.6, 0.25],  # medium NDVI
    [0.05, 0.2, 0.70],  # low NDVI
])
model.set_observation_model(A)

B = np.array([
    [0.85, 0.10, 0.02],
    [0.10, 0.75, 0.18],
    [0.05, 0.15, 0.80],
])
model.set_transition_model(B)

D = np.array([0.33, 0.34, 0.33])
model.set_state_prior(D)

# Step 3: Create agent and process observations
agent = ActiveInferenceModel(model_type="categorical")
agent.set_generative_model(model)

observation = np.array([0.7, 0.2, 0.1])  # mostly high NDVI
beliefs = agent.perceive(observation)

calculator = FreeEnergyCalculator()
fe = calculator.compute_categorical_free_energy(beliefs, observation)
print(f"Updated beliefs: {beliefs}")
print(f"Free energy: {fe:.4f}")
```

## Technical Standards

### Key Technical Decisions

These decisions apply across all 44 modules and are documented in the root
`.cursorrules/` directory:

- **H3 v4**: All modules use `h3>=4.0.0` with the v4 API (`latlng_to_cell`,
  `cell_to_latlng`). The legacy v3 API (`geo_to_h3`, `h3_to_geo`) is not used.
- **PEP 8 lowercase packages**: All 44 modules use `geo_infer_module` (lowercase)
  naming convention.
- **Real implementations**: No placeholder stubs, no `pass` in functional code.
  The `pass` keyword appears only in abstract methods, exception handlers, and
  import guards.
- **Graceful degradation**: Each `__init__.py` uses `try/except` for optional
  dependency imports, so modules remain importable even when optional packages
  are missing.
- **EPSG:4326 default**: All spatial data uses WGS84 as the default CRS unless
  an operation specifically requires a projected CRS.
- **Type annotations**: All function signatures include parameter types and
  return types.
- **Google-style docstrings**: Used across all Python code.

### Testing Standards

- Every module has a minimum of 4 test files.
- Tests use pytest markers: `unit`, `integration`, `system`, `performance`,
  `geospatial`, `api`, `slow`, `fast`.
- The unified test runner at `GEO-INFER-TEST/run_unified_tests.py` discovers
  and executes tests across all modules.
- Real implementations over mocks: integration tests use actual dependencies
  where feasible.

### Code Quality Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| Black | Code formatting | Line length 88, in `pyproject.toml` |
| isort | Import sorting | Profile "black", in `pyproject.toml` |
| mypy | Type checking | Strict mode, in `pyproject.toml` |
| flake8 | Linting | Standard rules, in `pyproject.toml` |
| pytest | Testing | Markers and config in `pytest.ini` |

## Getting Started

### For Researchers

1. Install core modules: MATH, ACT, BAYES, SPACE, TIME
2. Read the [Active Inference Guide](active_inference_guide.md)
3. Work through the [Bayesian Inference Guide](bayesian_inference_guide.md)
4. Explore domain modules relevant to your field
5. Run the quick start example above to verify everything works

### For Developers

1. Clone the repository and install the dev environment
2. Read the [Documentation Guide](documentation_guide.md) for contribution standards
3. Study the [Data Dictionary](data_dictionary.md) for API conventions
4. Run tests: `uv run python -m pytest GEO-INFER-MATH/tests/ -v`
5. Explore the [Examples Gallery](examples_gallery.md)
6. Use the [Module README Template](module_readme_template.md) when creating modules

### For Analysts

1. Install core modules plus your domain module (e.g., AG, CLIMATE, RISK)
2. Read the [Installation Guide](installation.md)
3. Follow examples in the [Examples Gallery](examples_gallery.md)
4. Reference the [Geospatial Standards](geospatial_standards.md) for data formats
5. Consult the [Terminology Glossary](terminology.md) for unfamiliar terms

## Framework Evolution

GEO-INFER evolves through modular extension. New domain modules can be added
without modifying existing code:

1. Create the module directory: `GEO-INFER-NEWMODULE/`
2. Follow the [Module README Template](module_readme_template.md)
3. Add `SKILL.md`, `AGENTS.md`, and `pyproject.toml`
4. Implement against the interfaces defined in foundation modules
5. Add tests and register with the unified test runner

The dependency graph ensures that adding a new domain module at Layer 4 never
requires changes to Layer 0-2 modules.

## Related Documentation

- [Installation Guide](installation.md)
- [Active Inference Guide](active_inference_guide.md)
- [Bayesian Inference Guide](bayesian_inference_guide.md)
- [Geospatial Standards](geospatial_standards.md)
- [Data Dictionary](data_dictionary.md)
- [Examples Gallery](examples_gallery.md)
- [Terminology Glossary](terminology.md)
- [Documentation Guide](documentation_guide.md)
- [Module README Template](module_readme_template.md)
