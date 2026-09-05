# GEO-INFER Open Task & Backlog Ledger

> Last reviewed: 2026-09-04
> Scope: Multi-package repository (`GEO-INFER`) across workspace packages and 44 domain modules.
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
| **DOCS-01** | INTRA / deferred browser verification | [DEFERRED-VERIFY] With a connected Interceptor browser, exercise the 44-preview index and representative module pages: online Leaflet map, tile/CDN failure, offline SVG fallback, narrow viewport, keyboard navigation and accessible labels. | Save browser/viewport versions, screenshots and observed interaction results; link/map controls and fallback remain usable, no relevant console errors, and asset receipts still match all 44 bundles. Extend checks to any page-specific failures. |
| **CI-01** | Repository / recurring hosted verification | Observe the exact pushed SHA on hosted Python 3.11/3.12 Linux CI; exercise clean wheel verification through the existing nonpublishing workflow when needed. | Required jobs pass for that SHA, with logs/artifacts retained by CI. Local macOS/Linux ARM64 results do not substitute for hosted x86 results. Fix attributable failures before considering this item complete; creating a version tag or external package publication requires a separate release decision. |
| **PLACE-V14** | PLACE / regional layer acquisition open | Three source-backed layers are delivered (13 HU4 display polygons, 24 volcanoes, one convergent boundary). Obtain the remaining complete licensed `cascadia_bioregion_boundary.geojson`; retain the documented per-layer extent and interpretation. | Validate WGS84, required geometry types, stable feature identifiers, provenance and checksums; run actual-data renderer/integration checks. Keep missing-layer behavior explicit until data exists. Do not restore the former 12-volcano or earthquake-probability claims without evidence. |
| **PLACE-03** | PLACE / request isolation follow-up | Add an isolated acquisition worker with a parent-enforced wall-clock deadline and process cleanup; current five-minute request budget is cooperative between response chunks. | A slow-drip server cannot exceed the parent deadline or leave a downloader running; preserve byte/feature caps and deterministic offline replay. Current bounded connect/read inactivity timeouts are not a strict elapsed-time guarantee. |
| **PERF-01** | TEST / optional import-latency investigation | Reproduce native ART/pandas import latency in a clean macOS environment with installation and import times separated; compare default and hardlink installs under controlled cache/load conditions. | Retain native stacks, dependency/OS versions and repeated cold/warm timings. Investigate the observed 120-second timeouts without weakening OS validation or relabeling the successful 600-second correctness bound as a performance fix. No current import-speed guarantee. |
| **CODE-01** | Repository / recurring index refresh | GEO symbol lookup was verified at `2b6d669e`. GNN remains indexed at `89f3b5e`: final refresh at `ffebd394` failed after one FTS repair attempt. Rebuild or repair the disposable GNN index, verify explicit exporter lookups, then refresh against the subsequently published commits. | Require indexed/current commit parity plus correct explicit-file Gaussian exporter and sparse-transition lookups; inspect unexpected callers/flows. Keep direct source/caller review as the fallback with reduced GNN graph confidence until that evidence exists. |

## Delivered capabilities

| ID | Area | Completed scope and evidence |
| --- | --- | --- |
| **ARCH-01** | Packaging | All 44 domain wheels have metadata and source/resource inventory checks, clean isolated installation, origin/version/resource probes, bounded process cleanup and completion receipts. Locked Python 3.11/3.12 wheel checks passed on macOS and Linux ARM64; hosted verification is tracked in CI-01. |
| **TIME-01** | TIME | Real WebSocket/Kafka adapters, explicit replay, bounded event-time buffers, watermark/session/sliding windows, anomaly integration and commit-after-processing. Real local WebSocket and Kafka delivery/replay/resume checks passed. [Migration guide](GEO-INFER-TIME/docs/streaming_migration.md). |
| **PLACE-01** | PLACE | Installable resumable USGS loader and checksummed 34-reach lower Smith River pilot, with native IDs and full topology before filtering. The expanded envelope is PLACE-02 below; full-region coverage is not claimed and the missing regional boundary remains PLACE-V14. |
| **PLACE-02** | PLACE | Expanded bounded lower Smith envelope: 59 source reaches, native IDs, checksums and repeat-cache/topology receipts in [ACQUISITION.md](GEO-INFER-PLACE/src/geo_infer_place/hydrography/data/smith_expanded/ACQUISITION.md). Further scaling requires a new bounded acquisition plan. |
| **GNN-04** | Cross-repository CI | Hosted pinned pairing passed on Python 3.11 and 3.12 at GEO `b0c07568` / GNN `89f3b5e79`, covering categorical/H3/Gaussian/factored artifacts in independent locked environments. [Run and receipts](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33938901328). |
| **TEST-02** | Windows/Linux probes | All 43 source/wheel subprocess regressions passed on Windows and Linux, Python 3.11/3.12, at GEO `6630aaf3`; each Windows run verified parent/child termination. [Hosted receipts](https://github.com/ActiveInferenceInstitute/GEO-INFER/actions/runs/33939067638). |
| **SPACE-01 implementation** | SPACE | Lazy device selection, bounded numeric distance joins, float64 CPU references, stable grouping and honest H3 host-topology reporting. Physical-device verification remains SPACE-01 above. |
| **DOCS-01 implementation** | INTRA | All 44 deterministic HTML/SVG/PNG bundles show computed H3 geometry, illustrative-data labels, artifact checksums and offline fallback. Browser interaction remains DOCS-01 above. |

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

The [September review ledger](GEO-INFER-TEST/docs/hardening_2026_09.md) records baseline, final checks, API migrations and verification limits.


## GNN interoperability follow-up (September 2026)

| ID | Scope | Acceptance evidence |
| --- | --- | --- |
| TEST-GNN-01 | Investigate the observed Python 3.12 PROJ SQLite disk-I/O failure during the combined ACT/SPACE/TIME test process. A fresh integrity probe and all 587 SPACE tests passed separately. | Capture a minimal import/order reproduction, loaded PROJ/GDAL/SQLite versions and file-descriptor state; correct a reproducible cause without suppressing CRS tests or declaring an unverified environment fix. |
| INTEGRATE-GNN-01 | Merge the GEO and GNN topic branches with their concurrently advancing main checkouts. GNN's topic starts from the existing local fleet baseline `64d49355`. | Preserve concurrent parser/security/module refactors, review ancestry, rerun the paired contract command at the merged revisions, and verify both remote SHAs. |

## September expansion delivered

Gaussian and explicitly factored contracts, Step 7 metadata/CLI, sparse H3
transfers, irregular action schedules and legacy observation timing are
implemented and independently reviewed. Evidence and remaining external
verification are in [the continuation receipt](GEO-INFER-TEST/docs/gnn_continuation_2026_09.md).
The physical GPU, full native keyboard/browser checks, missing licensed
bioregion boundary, controlled import-performance investigation and unexplained
historical PROJ failure remain open; implementation is not substituted for
those empirical checks. Hosted CI and PR merge status are tracked separately.
