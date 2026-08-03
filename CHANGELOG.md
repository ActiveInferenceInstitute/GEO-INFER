# GEO-INFER Changelog

All notable changes to the GEO-INFER framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **GeoLibre integration (`.geolibre.json` project writer)** in
  `GEO-INFER-SPACE.core.geolibre_projects`: deterministic, schema-versioned
  project emission (v0.1.0) with GeoJSON/tile layer builders, styled H3 grid
  export (`build_h3_grid_project`), and receipt-compatible writing. GEO-INFER
  results now open directly in the GeoLibre web/desktop/Jupyter viewer with no
  JavaScript added to the repository.
- **H3 resolution policy** in `GEO-INFER-SPACE.core.h3_policy`: pure helpers
  for H3 resolution suggestion (`suggest_h3_resolution`) and a hard-cell-cap
  guard (`check_cell_budget`) mirroring GeoLibre's H3 grid guard; a combined
  `suggest_resolution_with_budget` convenience wrapper.
- **Processing algorithm registry** in `GEO-INFER-SPACE.core.algorithm_registry`:
  a GeoLibre-style `ProcessingAlgorithm`/`AlgorithmRegistry` surface (id, name,
  description, parameters, run/context) with reference algorithms
  (`calculate-bounds`, `count-features`) so SPACE/API/APP can expose spatial
  tools uniformly.
- **Optional WhiteboxTools bridge** in `GEO-INFER-SPACE.core.whitebox_bridge`:
  graceful `HAS_WHITEBOX` probe and a representative `flow_accumulation`
  terrain helper for WATER/FOREST/EMERGENCY domain modules.
- **Cloud-native vector readers** in `GEO-INFER-DATA.utils.duckdb_spatial`:
  GeoParquet/FlatGeobuf/Shapefile reading via DuckDB-Spatial when available,
  transparent GeoPandas/Fiona fallback otherwise (`read_cloud_native_vector`).
- **LLM proxy policy** in `GEO-INFER-AGENT.core.llm_proxy`: dependency-free
  model allowlist, request-size cap, output-token cap, and per-client rate
  limiting (mirrors GeoLibre's `ai-proxy` shape) for server-side LLM serving.
- **geolibre export example**:
  `GEO-INFER-EXAMPLES/examples/getting_started/geolibre_export/` — runnable
  end-to-end demo emitting a styled `.geolibre.json` H3 grid project.
- Documentation hub refresh covering installation, first spatial inference,
  architecture, module selection, H3 v4 usage, developer workflow, testing,
  and contribution guidance.
- Root documentation map linking conceptual INTRA guides to source-backed
  module README/SKILL files and executable GEO-INFER-TEST gates.

- Unified test runner `GEO-INFER-TEST/run_unified_tests.py` with `--module`, `--category`, and `--h3-migration` flags
- Cross-module integration tests covering SPACE↔TIME, AGENT↔ACT, and DATA↔API interactions
- `WATER` module WQI calculation and 2D Gaussian pollution plume modeling
- `MARINE` module ocean monitoring, Blue Carbon estimation, and Marine Protected Area analysis
- `FOREST` module NDVI health monitoring, wildfire risk index (FWI), and carbon sequestration
- `ENERGY` module renewable site suitability mapping and LCOE benchmarking
- `CLIMATE` module climate change adaptation modeling with Bayesian uncertainty quantification

### Changed

- **PEP 8 package naming normalization completed** — all 44 modules now use lowercase `geo_infer_<module>` package directories (`geo_infer_forest`, `geo_infer_marine`, `geo_infer_energy`, `geo_infer_water` included). Stale docs referencing mixed-case paths corrected.
- **TIME module**: `sklearn` now guarded with a `HAS_SKLEARN` flag and `LinearRegression` raises an actionable `RuntimeError` when unavailable; `requirements.txt` lists `scikit-learn>=1.6.1` to match `pyproject.toml`.
- **BAYES module**: Full-rank variational inference now uses a scalar Cholesky covariance approximation; vector-valued full-rank parameters raise a clear `ValueError`, while mean-field inference remains available for vector parameters.
- **COMMS module**: REST models now use the repository's Pydantic v2/FastAPI contract, preserve intentional HTTP errors, and isolate per-instance CORS configuration.
- **Repository toolchain**: Module-level mypy configurations now target the supported Python 3.11 baseline consistently.

### Fixed

- Documentation drift: README, CLAUDE.md, AGENTS.md and module-level docs updated to reflect completed lowercase normalization.
- Replaced stale INTRA navigation and examples that referenced nonexistent
  API, deployment, workflow, and package paths with current repository links.

---

## [0.2.0] - 2026-02-25

### Added

- PAI Algorithm integration (`PAI.md`): 7-phase OBSERVE→LEARN methodology for GEO-INFER development
- `GEO-INFER-SPM`: Statistical Parametric Mapping module (spatial GLM, random field theory)
- `GEO-INFER-EXAMPLES`: Cross-module integration demonstrations and entry-point tutorials
- Module-specific `.cursorrules` files extending root rules for all 44 modules
- Root-level `.cursorrules/` directory with framework-wide development rules
- Backend-agnostic spatial dispatch pattern (`SpatialIndexingInterface`) in SPACE module

### Changed

- **SPACE module**: Fully migrated to H3 v4 API (`latlng_to_cell`, `cell_to_latlng`, `geo_to_cells`)
- **PLACE module**: Fully migrated to H3 v4 API (FULLY MIGRATED status)
- **Environmental modules**: Groundwork for lowercase package dir normalization landed (completed in Unreleased).
- **Zero-Mock Policy**: Enforced across all 44 modules — every function has real algorithmic logic
- **BAYES module**: GaussianProcess upgraded to real Cholesky decomposition; model comparison uses LOO/WAIC/DIC/BIC/AIC
- **ACT module**: Free energy calculation hardened with proper NumPy array handling
- License standardized to CC BY-NC-SA 4.0 across all 44 modules
- All 44 modules now maintain minimum 4 test files (unit, integration, performance, system)

### Fixed

- Interpolation bug in `GEO-INFER-TIME` temporal analysis
- F-string formatting issues in `GEO-INFER-AI` and `GEO-INFER-COG`
- Import compatibility issues in `GEO-INFER-AGENT` and `GEO-INFER-ANT`
- 13 source bugs across applied domain modules (HEALTH, ECON, RISK, AG, BIO)
- 7 source bugs across governance modules (NORMS, METAGOV, SEC, COMMS)
- Zero illegitimate `pass` stubs (remaining `pass` only in abstract methods, exception handlers, import guards)

---

## [0.1.0] - 2026-01-26

### Added

- Initial release of GEO-INFER framework
- **Core Modules**:
  - GEO-INFER-ACT: Active Inference implementation
  - GEO-INFER-BAYES: Bayesian inference and probabilistic modeling
  - GEO-INFER-SPACE: Spatial operations and H3 indexing
  - GEO-INFER-TIME: Temporal analysis and forecasting
  - GEO-INFER-DATA: Data management and ETL
  - GEO-INFER-MATH: Mathematical foundations
  - GEO-INFER-AI: Machine learning and deep learning

- **Agent Framework**:
  - GEO-INFER-AGENT: Agent orchestration
  - GEO-INFER-ANT: Swarm intelligence
  - GEO-INFER-NORMS: Normative reasoning
  - GEO-INFER-METAGOV: Meta-governance

- **Domain Applications**:
  - GEO-INFER-AG: Precision agriculture
  - GEO-INFER-BIO: Biodiversity and ecology
  - GEO-INFER-CLIMATE: Climate analysis
  - GEO-INFER-ECON: Spatial economics
  - GEO-INFER-EDU: Educational technology
  - GEO-INFER-EMERGENCY: Emergency management
  - GEO-INFER-ENERGY: Energy systems
  - GEO-INFER-FOREST: Forest monitoring
  - GEO-INFER-HEALTH: Public health
  - GEO-INFER-LOG: Logistics and supply chain
  - GEO-INFER-MARINE: Marine analysis
  - GEO-INFER-RISK: Risk assessment
  - GEO-INFER-TRANSPORT: Transportation
  - GEO-INFER-WATER: Water resources

- **Infrastructure**:
  - GEO-INFER-API: API infrastructure
  - GEO-INFER-APP: Application development
  - GEO-INFER-COMMS: Communications
  - GEO-INFER-IOT: IoT integration
  - GEO-INFER-OPS: DevOps and operations
  - GEO-INFER-SEC: Security
  - GEO-INFER-TEST: Testing framework

- **Visualization & UX**:
  - GEO-INFER-ART: Cartographic design
  - GEO-INFER-COG: Cognitive spatial reasoning
  - GEO-INFER-CIV: Civic engagement
  - GEO-INFER-PLACE: Place-based analysis

- **Analysis**:
  - GEO-INFER-SIM: Simulation framework
  - GEO-INFER-SPM: Statistical parametric mapping

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.2.0 | 2026-02-25 | Second beta release |
| 0.1.0 | 2026-01-26 | Initial release |

---

The version labels above are historical documentation entries. The current
checkout does not carry matching Git tags, so release comparison links are not
published here; use the repository commit history and GitHub releases page
when release metadata is available.
