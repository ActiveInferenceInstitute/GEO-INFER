---
name: geo-infer
description: Geospatial Active Inference framework with 44 modules for ecological, civic, and commercial spatial analysis. Use when working with geospatial data, Active Inference, Bayesian modeling, H3 hexagonal indexing, spatial statistics, or any domain-specific geographic analysis (agriculture, health, economics, risk, climate, energy, transport, marine, forestry, water).
---

# GEO-INFER

A 44-module Python monorepo implementing Active Inference principles for geospatial analysis.

## Instructions

### Module Discovery

Modules are in `GEO-INFER-{NAME}/` directories. Each has its own `SKILL.md` for detailed guidance.

#### Analytical Core

| Module | Import | Purpose |
|--------|--------|---------|
| MATH | `geo_infer_math` | Spatial statistics, topology, graph theory |
| ACT | `geo_infer_act` | Active Inference (free energy, belief updating) |
| BAYES | `geo_infer_bayes` | Bayesian inference (PyMC, TFP, variational) |
| AI | `geo_infer_ai` | ML pipelines, model selection, spatial features |
| COG | `geo_infer_cog` | Cognitive modeling (attention, memory, trust) |
| SPM | `geo_infer_spm` | Statistical Parametric Mapping (GLM, RFT) |

#### Spatial-Temporal & Infrastructure

| Module | Import | Purpose |
|--------|--------|---------|
| SPACE | `geo_infer_space` | H3 v4 hexagonal indexing, spatial backends |
| TIME | `geo_infer_time` | Time series, temporal analysis, forecasting |
| IOT | `geo_infer_iot` | IoT sensor ingestion (MQTT, streaming) |
| DATA | `geo_infer_data` | ETL pipelines, connectors, format loaders |
| API | `geo_infer_api` | FastAPI REST/GraphQL endpoints |
| SEC | `geo_infer_sec` | Security, threat detection, access control |
| OPS | `geo_infer_ops` | Monitoring, alerting, observability |

#### Domain Modules

| Module | Import | Purpose |
|--------|--------|---------|
| AG | `geo_infer_ag` | Agriculture, soil health, carbon (IPCC Tier 1) |
| HEALTH | `geo_infer_health` | Epidemiology, health access, SaTScan |
| ECON | `geo_infer_econ` | Bioregional markets, call auctions |
| RISK | `geo_infer_risk` | Catastrophe models, Monte Carlo loss |
| LOG | `geo_infer_log` | Logistics, routing, supply chain (PuLP) |
| BIO | `geo_infer_bio` | Biodiversity, habitat connectivity |
| CLIMATE | `geo_infer_climate` | Climate projections, SPI/PDSI indices |
| ENERGY | `geo_infer_energy` | LCOE, renewable siting, grid analysis |
| FOREST | `geo_infer_forest` | Forest cover, carbon stocks, wildfire |
| MARINE | `geo_infer_marine` | Ocean currents, coastal, MPA planning |
| EMERGENCY | `geo_infer_emergency` | SAR, disaster response, evacuation |
| TRANSPORT | `geo_infer_transport` | Traffic (BPR), EWMA forecasting, emissions |
| WATER | `geo_infer_water` | Watershed, hydrology, flood risk |

#### Agents & Simulation

| Module | Import | Purpose |
|--------|--------|---------|
| AGENT | `geo_infer_agent` | Multi-agent systems, telemetry |
| ANT | `geo_infer_ant` | ACO, PSO, ABC swarm optimization |
| SIM | `geo_infer_sim` | Agent-based simulation, Monte Carlo |

#### Community & Governance

| Module | Import | Purpose |
|--------|--------|---------|
| CIV | `geo_infer_civ` | Civic engagement, STEW-MAP |
| PEP | `geo_infer_pep` | Public engagement, CRM |
| ORG | `geo_infer_org` | Organizational modeling |
| COMMS | `geo_infer_comms` | Messaging, notifications, spatial routing |
| METAGOV | `geo_infer_metagov` | Polycentric governance, Ostrom |
| NORMS | `geo_infer_norms` | Compliance, normative inference (Jaccard) |
| REQ | `geo_infer_req` | Requirements, traceability, P3IF |

#### Presentation & Operations

| Module | Import | Purpose |
|--------|--------|---------|
| APP | `geo_infer_app` | Dashboards, agent widgets, map views |
| ART | `geo_infer_art` | Generative geo-art, cartographic design |
| EDU | `geo_infer_edu` | Curricula, exercises, assessment |
| PLACE | `geo_infer_place` | Geocoding, catchment analysis, H3 |
| GIT | `geo_infer_git` | Spatial data versioning, lineage |
| TEST | `geo_infer_test` | Unified test runner, fixtures, markers |
| EXAMPLES | `geo_infer_examples` | Orchestration patterns, workflows |
| INTRA | `geo_infer_intra` | Documentation hub, integration guides |

### Architecture & Data Flow

```text
┌──────────────────────────────────────────────────────────┐
│                      Data Sources                        │
│  (files, DBs, APIs, MQTT sensors)                        │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│              DATA / IOT (Ingestion Layer)                 │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│         SPACE / TIME / PLACE (Indexing Layer)             │
│  H3 v4 tessellation, CRS transforms, temporal indexing   │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│     MATH / BAYES / ACT / SPM (Analysis Layer)            │
│  Spatial statistics, Bayesian models, Active Inference    │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│    AI / AGENT / ANT / SIM (Intelligence Layer)           │
│  ML pipelines, agent systems, swarm optimization         │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│   Domain Modules (Application Layer)                     │
│  AG, HEALTH, ECON, RISK, LOG, BIO, CLIMATE, ENERGY,     │
│  FOREST, MARINE, EMERGENCY, TRANSPORT, WATER             │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│      API / APP / ART (Presentation Layer)                │
│  REST endpoints, dashboards, visualizations              │
└──────────────────────────────────────────────────────────┘
```

### Common Patterns

```python
# Graceful dependency imports (every __init__.py)
try:
    from .core.engine import Engine
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False

# H3 v4 API (never use legacy h3.geo_to_h3)
import h3
cell = h3.latlng_to_cell(lat, lng, resolution)
lat, lng = h3.cell_to_latlng(cell)

# Module installation
# uv pip install -e ./GEO-INFER-MATH
```

### Testing

```bash
# All modules
uv run python GEO-INFER-TEST/run_unified_tests.py

# Single module
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# With coverage
uv run python -m pytest GEO-INFER-MATH/tests/ --cov=GEO-INFER-MATH/src
```

### Modular Hygiene

```bash
uv sync --all-packages --all-extras
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
```

- Root `pyproject.toml`, `uv.lock`, and `.python-version` define the uv workspace.
- Each module keeps importable behavior under `src/` and at least four pytest files under `tests/`.
- Planned work belongs in root `TODO.md` or a tracked issue, not source or test task markers.
- Importable modules use `logging.getLogger(__name__)`; CLI entrypoints configure process-wide logging.

## Examples

### Cross-Module Pipeline

```python
from geo_infer_data.formats.geojson import GeoJSONLoader
from geo_infer_space.backends.h3 import H3Backend
from geo_infer_math.core.spatial_statistics import MoranI
from geo_infer_bayes.core.bayesian_inference import BayesianModel

# 1. Load data
features = GeoJSONLoader().load("observations.geojson")

# 2. Index to H3 cells
backend = H3Backend()
cells = backend.tessellate(features.bounds, resolution=7)

# 3. Compute spatial autocorrelation
moran = MoranI(values, weight_matrix)
result = moran.compute()

# 4. Bayesian parameter estimation
model = BayesianModel(prior="normal", likelihood="normal")
posterior = model.fit(data)
```

### Domain Workflow: Agricultural Risk

```python
from geo_infer_ag.models.soil_health import SoilHealthModel
from geo_infer_risk.core.risk_engine import RiskEngine
from geo_infer_space.backends.h3 import H3Backend

cells = H3Backend().tessellate(farm_polygon, resolution=9)
soil = SoilHealthModel()
health = {cell: soil.assess(cell) for cell in cells}
risk = RiskEngine().assess(hazard=drought_index, exposure=health)
```

### Active Inference Agent

```python
from geo_infer_agent.core.active_inference import ActiveInferenceAgent
import numpy as np

agent = ActiveInferenceAgent(n_states=8, n_observations=5, n_actions=4)
obs = np.random.dirichlet(np.ones(5))
action = agent.act(obs)
print(f"Action: {action}, Free energy: {agent.free_energy:.4f}")
```

## Guidelines

- **No mock/stub/placeholder code** — every function must have real logic
- **Active Inference first** — ground implementations in free energy minimization
- **Type hints everywhere** — full annotations on all parameters and returns
- **H3 v4 only** — use `latlng_to_cell`, not legacy `geo_to_h3`
- **Graceful degradation** — optional deps via `try/except ImportError`
- **Logger, not print** — use structured logging in all modules
- **Root task ledger** — use `TODO.md` or issues for future work; keep source and tests free of task markers
- **uv workspace hygiene** — keep root `pyproject.toml`, `.python-version`, and `uv.lock` as the shared environment contract
- Check each module's `SKILL.md` for domain-specific rules and integrations
