# GEO-INFER Changelog

All notable changes to the GEO-INFER framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### September 5 GNN, space/time and acquisition integration

- Add explicit GNN Gaussian and factored model contracts alongside categorical
  and H3 interchange, with bounded validation, source digests and reproducible
  inference traces. Preserve matrix axes, physical units and declared policies.
- Correct repeated observation conditioning during legacy policy evaluation;
  reject nonfinite policy scores and invalid covariance declarations.
- Add bounded sparse H3 transitions and conservative resolution transfers,
  including pentagons. Irregular temporal observations require explicit
  intervening actions and exact prediction counts.
- Extend source-backed regional display layers and the checksummed lower Smith
  envelope to 59 reaches. Supervise regional HTTP acquisition in an isolated
  process with a parent-enforced deadline and bounded cleanup.
- Pin the merged GNN companion revision. Run paired-contract and Linux/Windows
  import-probe checks on main pushes, and retain test-category artifacts before
  the unified runner cleans its output directory.
- Record verified main integration separately from physical GPU, complete browser,
  licensed-boundary and Windows regional-worker verification in [TODO.md](TODO.md).



### September 4 hardening and integration

- Deliver real WebSocket/Kafka ingestion with explicit replay and acknowledgements
  after processing; preserve upstream adapter injection and broker timestamps.
- Add lazy GPU capability checks, bounded float64 spatial kernels and explicit
  host-only H3 topology diagnostics. Physical GPU validation remains deferred.
- Package resumable, checksummed USGS hydrography acquisition and a 34-reach lower
  Smith River pilot; retain explicit missing-data, offline and projection controls.
- Regenerate all 44 H3 preview bundles with deterministic geometry/assets,
  illustrative-data labels, provenance and an offline fallback.
- Replace unrestricted raster expression execution with a bounded allowlisted AST;
  reject filesystem access, output mutation and incompatible raster alignment.
- Verify fresh wheel metadata, code and resources; require complete isolated-import
  receipts and terminate timed-out process groups. Keep dependency parity and
  passive-logging gates from the upstream integration.
- Align runtime versions with distribution metadata, fix CI formatting and merge
  the upstream fix wave without rewriting published history.
- Document API migrations and separate deferred verification from regional data
  acquisition in [TODO.md](TODO.md). See the [review ledger](GEO-INFER-TEST/docs/hardening_2026_09.md)
  for pre-merge and combined-tree evidence and platform limits.

### Added

- A dated validation receipt for the 2026-08-13 performance and isolated
  module-coverage campaign, including failed-attempt evidence, optional-backend
  availability, artifact digests, and the all-extras CuPy build boundary.
- Typed, redacted email-provider delivery failures and regression tests for
  SMTP, SendGrid, and AWS SES integrations.
- A deterministic Cascadia validation profile shared by the focused and
  comprehensive compatibility entry points.
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


### Changed and Fixed (2026-09-02 fix wave)

- Merged `codex/act-categorical-runtime` hardening into `main`; the
  2026-09-02 fix wave then applied real-implementation, contract, and
  hygiene corrections across all modules, with the repository validators
  (`validate_test_contracts.py --strict`, `validate_model_contracts.py
  --strict --seed 42`, `run_model_audit.py --seed 42 --reproducible`,
  `validate_active_inference_contract.py`) re-run against the result.
- **MATH**: replaced simplified numerics with real implementations for
  kriging, CP and Tucker tensor decompositions, BA estimation, and theorem
  verification; added a unified Moran variance implementation used across
  the spatial-statistics paths.
- **DATA**: added SQL/GraphQL identifier validation on query surfaces and
  restricted decompression to envelope payloads only.
- **API**: required `SECRET_KEY` for signed operations and hardened CORS
  configuration.
- **TIME**: replaced mock stream transports with real WebSocket and Kafka
  adapters behind the optional `streaming` extra (`websockets`, `aiokafka`).
- **EMERGENCY**: replaced simplified evacuation routing with a real
  `networkx`-based routing implementation.
- **SIM**: fixed the pause/resume state machine so transitions respect the
  declared run states.
- **LOG**: restored compatibility with `networkx` 3.x APIs.
- **RISK**: implemented the previously missing-but-advertised `api`
  (`RiskAPI`, `ModelRegistry`, `ResultsFormatter`) and peril-model export
  surfaces against the existing engine, with export-contract tests.
- **ECON**: removed duplicate shadowing class definitions and the undefined
  `ConsumerTheoryModels` export so every `__all__` name resolves.
- **COG**/**AI**: threaded deterministic seeded `np.random.Generator`
  instances through stochastic code paths.
- **OPS**: reduced module-level logging to a single `getLogger(__name__)`
  entry point.
- **HEALTH**/**CLIMATE**/**MARINE**/**TRANSPORT**/**FOREST**/**EDU**/**WATER**:
  module-specific real-implementation, contract, and hygiene fixes from the
  same fix wave.
- **EXAMPLES**: replaced placeholder orchestration scripts with real
  end-to-end module orchestrators.

### Changed

- The unified coverage runner now executes each module in an isolated pytest
  subprocess, rejects skips/xfails from JUnit evidence, emits aggregate
  coverage JSON, and removes stale per-module receipts before a run.
- GEO-INFER-AI spatial feature transforms reuse the training centroid and
  clear it on a coordinate-free refit; RISK cross-validation now evaluates a
  fitted mean-loss baseline per fold and validates finite samples.
- Cascadia configuration and validation no longer depend on the caller's
  working directory; the ownership data source resolves its tracked URL
  configuration from the framework root.
- **PEP 8 package naming normalization completed** — all 44 modules now use lowercase `geo_infer_<module>` package directories (`geo_infer_forest`, `geo_infer_marine`, `geo_infer_energy`, `geo_infer_water` included). Stale docs referencing mixed-case paths corrected.
- **TIME module**: `sklearn` now guarded with a `HAS_SKLEARN` flag and `LinearRegression` raises an actionable `RuntimeError` when unavailable; `requirements.txt` lists `scikit-learn>=1.6.1` to match `pyproject.toml`.
- **BAYES module**: Full-rank variational inference now uses a scalar Cholesky covariance approximation; vector-valued full-rank parameters raise a clear `ValueError`, while mean-field inference remains available for vector parameters.
- **COMMS module**: REST models now use the repository's Pydantic v2/FastAPI contract, preserve intentional HTTP errors, and isolate per-instance CORS configuration.
- **Repository toolchain**: Module-level mypy configurations now target the supported Python 3.11 baseline consistently.

### Fixed

- Removed stale COMMS integration exports for modules that do not exist and
  corrected MIME imports used by real email attachments.
- Replaced vacuous/skipped Cascadia validation scripts with strict real
  backend, H3, configuration, and module-initialization checks.
- Corrected the INTRA system-test workspace root, removed a wall-clock HEALTH
  assertion, and made root matplotlib cleanup explicit and test-covered.
- Strict repository terminology no longer mistakes completed SIM acceptance
  evidence for module-local planned work.
- Documentation drift: README, CLAUDE.md, AGENTS.md and module-level docs updated to reflect completed lowercase normalization.
- Replaced stale INTRA navigation and examples that referenced nonexistent
  API, deployment, workflow, and package paths with current repository links.
- WATER pollution plume dispersion now derives its grid extent from
  `grid_resolution`, computes `plume_area_km2` from the actual grid cell size
  instead of the nominal resolution, and guards zero diffusion/time so
  concentration fields stay finite and the reported area is no longer
  underestimated.

---

## [0.2.0] - 2026-02-25

### Added

- PAI Algorithm integration (`PAI.md`): 7-phase OBSERVE→LEARN methodology for GEO-INFER development
- `GEO-INFER-SPM`: Statistical Parametric Mapping module (spatial GLM, random field theory)
- `GEO-INFER-EXAMPLES`: Cross-module integration demonstrations and entry-point tutorials
- Root-level `.agents/` directory with framework-wide development rules and standards
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

[Unreleased]: https://github.com/ActiveInferenceInstitute/GEO-INFER/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ActiveInferenceInstitute/GEO-INFER/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ActiveInferenceInstitute/GEO-INFER/releases/tag/v0.1.0
