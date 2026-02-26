# GEO-INFER Changelog

All notable changes to the GEO-INFER framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Unified test runner `GEO-INFER-TEST/run_unified_tests.py` with `--module`, `--category`, and `--h3-migration` flags
- Cross-module integration tests covering SPACE↔TIME, AGENT↔ACT, and DATA↔API interactions
- `WATER` module WQI calculation and 2D Gaussian pollution plume modeling
- `MARINE` module ocean monitoring, Blue Carbon estimation, and Marine Protected Area analysis
- `FOREST` module NDVI health monitoring, wildfire risk index (FWI), and carbon sequestration
- `ENERGY` module renewable site suitability mapping and LCOE benchmarking
- `CLIMATE` module climate change adaptation modeling with Bayesian uncertainty quantification

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
- **Environmental modules**: Package directories renamed to PEP 8 lowercase (`geo_infer_forest`, `geo_infer_marine`, `geo_infer_energy`, `geo_infer_water`)
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

[Unreleased]: https://github.com/ActiveInferenceInstitute/GEO-INFER/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ActiveInferenceInstitute/GEO-INFER/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ActiveInferenceInstitute/GEO-INFER/releases/tag/v0.1.0
