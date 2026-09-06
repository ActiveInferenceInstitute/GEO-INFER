# GEO-INFER Open Task & Backlog Ledger

> Last reviewed: 2026-09-05
> Scope: Multi-package repository (`GEO-INFER`) across workspace packages and 45 domain modules.
> Centralization Rule: All planned, open, or deferred engineering work across all modules is tracked exclusively in this ledger. Module source code and tests must never carry local task markers (`TODO`, `FIXME`, `XXX`, `HACK`).

---

## Open work and acceptance criteria

Completed implementation and deferred verification are tracked separately below.
Module names identify the responsible area, not an assigned person. Acquisition
items require an explicit area, source and resource budget before running them;
this ledger does not authorize full-region downloads or a package release.

| ID | Area / status | Bounded next step | Acceptance evidence / dependencies |
| --- | --- | --- | --- |
| **SPACE-01** | SPACE / deferred hardware verification | [DEFERRED-VERIFY] On supported physical hardware, run numeric distance and grouped-reduction parity for each backend claimed as supported (CuPy, Torch, JAX), including empty inputs, float64 precision, chunk boundaries and allocation failure. Keep H3 topology labeled as host CPU. | Record device/driver/library versions, actual backend diagnostics, CPU-reference tolerances, peak memory and separate cold/warm timings. Publish speed claims only for measured workloads; do not infer support from CPU fallback. Requires hardware. [Guide](GEO-INFER-SPACE/docs/GPU_ACCELERATION.md). |
| **DOCS-01** | INTRA / deferred browser verification | [DEFERRED-VERIFY] With a connected Interceptor browser, exercise the 45-preview index and representative module pages: online Leaflet map, tile/CDN failure, offline SVG fallback, narrow viewport, keyboard navigation and accessible labels. | Save browser/viewport versions, screenshots and observed interaction results; link/map controls and fallback remain usable, no relevant console errors, and asset receipts still match all 45 bundles. Extend checks to any page-specific failures. |
| **PLACE-V14** | PLACE / regional layer acquisition open | Three source-backed layers are delivered (13 HU4 display polygons, 24 volcanoes, one convergent boundary). Obtain the remaining complete licensed `cascadia_bioregion_boundary.geojson`; retain the documented per-layer extent and interpretation. | Validate WGS84, required geometry types, stable feature identifiers, provenance and checksums; run actual-data renderer/integration checks. Keep missing-layer behavior explicit until data exists. Do not restore the former 12-volcano or earthquake-probability claims without evidence. |
| **PLACE-04** | PLACE / deferred Windows verification | [DEFERRED-VERIFY] Run the real regional download-worker loopback tests on Windows with the locked PLACE runtime. | Prove stalled-header/slow-drip deadlines, native process termination, pipe closure, batch failure preservation and exact replay on Windows; retain interpreter/OS versions. POSIX termination is verified and the worker starts no child processes. |
| **PERF-01** | TEST / optional import-latency investigation | Reproduce native ART/pandas import latency in a clean macOS environment with installation and import times separated; compare default and hardlink installs under controlled cache/load conditions. | Retain native stacks, dependency/OS versions and repeated cold/warm timings. Investigate the observed 120-second timeouts without weakening OS validation or relabeling the successful 600-second correctness bound as a performance fix. No current import-speed guarantee. |
| **CODE-01** | Repository / recurring index refresh | GNN index rebuilt successfully at merged `903b9c339`; Gaussian and factored exporter lookups resolve to the correct source files. GEO index/HEAD parity was verified at `2241e645`, with exact sparse-transition, parent-download and worker-fetch lookups. Refresh both indexes after subsequent commits and verify explicit lookups. | Require indexed/current commit parity plus correct explicit-file Gaussian exporter and sparse-transition lookups; inspect unexpected callers/flows. Use direct source/caller review when an index is stale or unavailable. |

## Delivered capabilities

| ID | Area | Completed scope and evidence |
| --- | --- | --- |
| **ARCH-01** | Packaging | All 44 domain wheels have metadata and source/resource inventory checks, clean isolated installation, origin/version/resource probes, bounded process cleanup and completion receipts. Locked Python 3.11/3.12 wheel checks passed on macOS and Linux ARM64; hosted verification passed at `e87c7703` (CI-01 below). |
| **TIME-01** | TIME | Real WebSocket/Kafka adapters, explicit replay, bounded event-time buffers, watermark/session/sliding windows, anomaly integration and commit-after-processing. Real local WebSocket and Kafka delivery/replay/resume checks passed. [Migration guide](GEO-INFER-TIME/docs/streaming_migration.md). |
| **PLACE-01** | PLACE | Installable resumable USGS loader and checksummed 34-reach lower Smith River pilot, with native IDs and full topology before filtering. The expanded envelope is PLACE-02 below; full-region coverage is not claimed and the missing regional boundary remains PLACE-V14. |
| **PLACE-02** | PLACE | Expanded bounded lower Smith envelope: 59 source reaches, native IDs, checksums and repeat-cache/topology receipts in [ACQUISITION.md](GEO-INFER-PLACE/src/geo_infer_place/hydrography/data/smith_expanded/ACQUISITION.md). Further scaling requires a new bounded acquisition plan. |
| **PLACE-03** | PLACE | Network acquisition runs in a private isolated worker with a parent-enforced five-minute batch deadline and a separate one-second cleanup budget. Real local HTTP tests cover slow-drip bodies, stalled headers, compressed byte caps, interruption, failure preservation and exact offline replay. Local geometry remains cooperative between phases; live Windows worker verification is PLACE-04 below. |
| **GNN-04** | Cross-repository CI | Hosted pinned pairing passed on Python 3.11 and 3.12 at GEO `cee1b5f08` / GNN `ffebd394b`, covering categorical/H3/Gaussian/factored artifacts in independent locked environments. [Run and receipts](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33941489772). |
| **INTEGRATE-GNN-01** | Main integration | [GNN PR 25](https://github.com/ActiveInferenceInstitute/GeneralizedNotationNotation/pull/25) merged at `903b9c339`; [GEO PR 8](https://github.com/ActiveInferenceInstitute/GEO-INFER/pull/8) merged at `6f15c100`. Reviewed ancestry is preserved, both remote main SHAs matched isolated checkouts, and original dirty checkouts remain untouched. All nine GEO pre-merge checks and the 44-wheel workflow passed; GNN post-merge CI passed. Subsequent exact-main runs remain the recurring CI-01 gate. |
| **TEST-02** | Windows/Linux probes | All 43 source/wheel subprocess regressions passed on Windows and Linux, Python 3.11/3.12, at GEO `cee1b5f08`; each Windows run verified parent/child termination. [Hosted receipts](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33941489777). |
| **SPACE-01 implementation** | SPACE | Lazy device selection, bounded numeric distance joins, float64 CPU references, stable grouping and honest H3 host-topology reporting. Physical-device verification remains SPACE-01 above. |
| **DOCS-01 implementation** | INTRA | All 45 deterministic HTML/SVG/PNG bundles show computed H3 geometry, illustrative-data labels, artifact checksums and offline fallback. Browser interaction remains DOCS-01 above. |
| **CONSOL-01** | Repository | Executed the three recorded structural candidates: civic-intel ingestion core consolidated canonically in BAYES (guarded delegation in ACT/RISK, single bundled contract JSON, identity + independence both test-pinned), the 1626-line `geospatial_ai` toolkit extracted from ACT to `geo_infer_ai.models.predictive` with its test suite, and the underwriting subsystem split out of RISK into the new GEO-INFER-INSURANCE module (45th; all count pins updated). Wheel receipts rebuilt on the final tree: 45 wheels, isolated-install import probes pass on Python 3.11 and 3.12. Source-language debt reworded to zero warnings. Evidence: the CHANGELOG "September 5 hardening ledger and compliance annex close-out" section (verification record, per-module fix table, structural item reports). |
| **COMPL-01** | Repository | 47-report per-module compliance/coherence audit (44 modules + import graph + backlog + root surfaces) and fix wave: all blocker/major findings fixed with regression tests, ~30 SKILL.md files rewritten to real APIs, ~20 broken examples repaired, packaging normalized (setup.py shims, phantom entry points removed, dependency ledgers corrected in both directions), undeclared cross-module dependencies declared, fabricated data replaced with real behavior, dead/stub surfaces deleted, placeholder tests replaced. Per-module suites pass; details in the September 5 CHANGELOG entry. |
| **DOCS-02** | INTRA | INSURANCE conceptual page ([geo-infer-insurance.md](GEO-INFER-INTRA/docs/modules/geo-infer-insurance.md), template-consistent, real API only with import-probed examples), modules/index.md catalog row, 45th deterministic preview bundle via the sanctioned builder (existing 44 bundles sha256-verified byte-identical), EXAMPLES gallery + orchestrator-registry entries, and a thin INSURANCE orchestrator that runs the real assess → underwrite → premium → claim flow end-to-end. |
| **HYG-01** | Repository | Cleanup-wave decision executed 2026-09-05: measured 1,030 F401/F841/F811 hits → 0 repo-wide. Per-site audit before every deletion (side-effect imports, try/except availability probes and externally-imported names preserved as redundant-alias re-exports); unused locals removed only for pure RHS; shadowed redefinitions removed. Sanctioned F821/F823/E721/E722 gate and compileall green post-wave. |
| **HYG-02** | Repository | Remove decision executed: untracked GEO-INFER-RISK/outputs/, GEO-INFER-NORMS/examples/output/ runtime artifacts and 18 stale __pycache__ files (moved/deleted sources) deleted; git status no longer reports the artifacts; zero tracked-file changes. |
| **CI-01** | Repository | Hosted recurring verification executed at `e87c7703` (Python 3.11/3.12 Linux x86): GEO-INFER CI (quality gate, repository contracts including packaging, full per-module pytest battery), import-probe portability, paired GNN interchange and dependency graph all pass. Merge-integration failures diagnosed and fixed in-flight: uv.lock resolved (c4586205), companion docs regenerated (1655b7b1), INSURANCE governance pin committed (24c4bf81), generator formatting canonicalized (da9c9453), INTRA package-data globs aligned (e87c7703). Wheel-verification exercise and release tagging remain separate decisions. |

---

## ✅ Completed & Verified Work (Audit Log)

1. **REPRO-01 (Completed)**: Explicit seeds use isolated `np.random.Generator` instances across `GEO-INFER-RISK` (`rng.py`), `GEO-INFER-BAYES` (`rng.py`), `GEO-INFER-MATH` (`rng.py`), and `GEO-INFER-SPM` (`rng.py`); unseeded SPM helpers retain their documented behavior, including the legacy global stream where promised.
2. **PLACE-V14 renderer correction (Completed)**: The renderer requires explicit WGS84 data or reports partial/unavailable layers when requested. Constructed geometry tests and tracked county boundaries verify the pipeline; actual regional acquisition and scientific coverage remain the open PLACE-V14 item above.
3. **SUPPLY-01 (Completed)**: Cleaned all installation references to point to verified editable installs (`uv pip install -e ./GEO-INFER-<MODULE>`).
4. **H3 v4.5 Composition (Completed)**: Implemented end-to-end multi-module composition suite (`test_h3_space_time_bayes_risk_act_composition.py`) connecting H3 spatial grids to `TIME`, `BAYES`, `RISK`, and `ACT`.
5. **BAYES-01 (Completed)**: Added batched inducing-point `SparseSpatialGP` regression with collapsed variational ELBO optimization, finite posterior uncertainty, and a 10,001-observation no-dense-covariance regression test.
6. **RISK-01 (Completed)**: Added directed multi-hazard interaction matrices and engine-level compound exceedance calculation for ordered hazard chains including earthquake to fire-following to flood.
7. **SPM-01 (Completed)**: Added full Gaussian Euler-characteristic inference across all boundary resel dimensions, peak FWE thresholds, topological cluster-extent FWE p-values, closed-form unit contracts, and fixed-seed known-null Monte Carlo calibration for both peak and cluster inference.
8. **SEC-01 (Completed)**: Added authenticated GISP1 HMAC-SHA256 serialization envelopes across `DATA` (`utils/secure_serialization.py`, `caching`, `storage`), `GIT` (`utils/secure_serialization.py`, `advanced_cache`), and `OPS` (`core/secure_serialization.py`, `cache`), with SEC integration coverage (`tests/integration/test_serialization_security.py`); unsigned, truncated, cross-context, and tampered payloads never reach a deserializer.
9. **ACT-01 (Completed)**: Added continuous POMDP Active Inference via a Laplace/Kalman-Bucy filter (`models/continuous_pomdp.py`) bridging discrete categorical and continuous-state Gaussian-filter inference, with free-energy-scored action selection and a focused unit test.
10. **MATH-01 (Completed)**: Added vectorized SIMD ray-casting point-in-polygon (`geometry.points_in_polygon_vectorized`) replacing iterative loops in spatial clustering.
11. **DATA-01 (Completed)**: Added cloud-connector byte-range reading (`connectors/cloud.py` `read_byte_range`) for chunked remote GeoParquet / Cloud-Optimized GeoTIFF access.
12. **TEST-01 (Completed)**: Added the parametric load benchmark harness (`tests/unit/test_parametric_load_benchmarks.py`) to the unified test runner's performance surface.

Baseline, final checks, API migrations and verification limits are preserved in the CHANGELOG September 5 hardening close-out section.
The [September review ledger](GEO-INFER-TEST/docs/hardening_2026_09.md) records baseline, final checks, API migrations and verification limits.


## GNN interoperability follow-up (September 2026)

| ID | Scope | Acceptance evidence |
| --- | --- | --- |
| TEST-GNN-01 | Investigate the observed Python 3.12 PROJ SQLite disk-I/O failure during the combined ACT/SPACE/TIME test process. A fresh integrity probe and all 587 SPACE tests passed separately. | Capture a minimal import/order reproduction, loaded PROJ/GDAL/SQLite versions and file-descriptor state; correct a reproducible cause without suppressing CRS tests or declaring an unverified environment fix. |

## September expansion delivered

Gaussian and explicitly factored contracts, Step 7 metadata/CLI, sparse H3
transfers, irregular action schedules and legacy observation timing are
implemented and independently reviewed. Evidence and remaining external
verification are in [the continuation receipt](GEO-INFER-TEST/docs/gnn_continuation_2026_09.md).
The physical GPU, full native keyboard/browser checks, missing licensed
bioregion boundary, controlled import-performance investigation and unexplained
historical PROJ failure remain open; implementation is not substituted for
those empirical checks. Hosted CI and PR merge status are tracked separately.
